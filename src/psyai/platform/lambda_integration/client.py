"""
Lambda Cloud GPU orchestration and inference client.

This module provides:
- On-demand Lambda instance launch
- Instance reuse for subsequent requests
- Idle auto-shutdown
- OpenAI-compatible chat completion calls against the hosted model server
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

import httpx

from psyai.core.config import get_settings
from psyai.core.exceptions import APIError, ConfigurationError, LLMError
from psyai.core.logging import get_logger
from psyai.core.utils.retry import retry_async

logger = get_logger(__name__)


def _utcnow() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def _parse_csv(value: str) -> List[str]:
    """Parse comma-separated values into a clean list."""
    return [part.strip() for part in value.split(",") if part.strip()]


def _iter_objects(value: Any) -> Iterable[Dict[str, Any]]:
    """Yield dictionaries recursively from nested JSON-like payloads."""
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _iter_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_objects(child)


def _extract_first_string(value: Any, keys: List[str]) -> Optional[str]:
    """Find first non-empty string (or first element from list) for candidate keys."""
    for obj in _iter_objects(value):
        for key in keys:
            if key not in obj:
                continue

            candidate = obj.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate
            if isinstance(candidate, list) and candidate:
                first = candidate[0]
                if isinstance(first, str) and first.strip():
                    return first

    return None


@dataclass
class LambdaInstanceState:
    """Cached Lambda instance state tracked in-process."""

    instance_id: Optional[str]
    instance_ip: Optional[str]
    status: Optional[str] = None
    launched_at: datetime = field(default_factory=_utcnow)
    last_used_at: datetime = field(default_factory=_utcnow)


@dataclass
class LambdaChatCompletion:
    """Result payload for a Lambda inference request."""

    content: str
    model: str
    latency_ms: float
    raw_response: Dict[str, Any]
    instance_id: Optional[str]
    instance_ip: Optional[str]


class LambdaGPUService:
    """Service for launching and using Lambda GPU-backed inference."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._instance_lock = asyncio.Lock()
        self._instance_state: Optional[LambdaInstanceState] = None

        self._cloud_client = httpx.AsyncClient(
            timeout=float(max(self.settings.lambda_launch_timeout_seconds, 30)),
            headers={"Content-Type": "application/json"},
        )
        self._inference_client = httpx.AsyncClient(
            timeout=float(max(self.settings.lambda_inference_timeout_seconds, 10)),
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"PsyAI/{self.settings.app_version}",
            },
        )

    def _cloud_url(self, path: str) -> str:
        """Build full Lambda Cloud API URL."""
        return f"{self.settings.lambda_cloud_base_url.rstrip('/')}/{path.lstrip('/')}"

    def _cloud_headers(self) -> Dict[str, str]:
        """Build Lambda Cloud API headers."""
        if not self.settings.lambda_cloud_api_key:
            raise ConfigurationError(
                "LAMBDA_CLOUD_API_KEY is required for Lambda GPU lifecycle operations"
            )

        return {
            "Authorization": f"Bearer {self.settings.lambda_cloud_api_key}",
            "Content-Type": "application/json",
        }

    def _resolve_inference_base_url(self, state: LambdaInstanceState) -> str:
        """Resolve base URL for inference calls."""
        if self.settings.lambda_inference_base_url:
            return self.settings.lambda_inference_base_url.rstrip("/")

        if not state.instance_ip:
            raise APIError("Lambda instance does not have a reachable IP address")

        return (
            f"{self.settings.lambda_inference_scheme}://"
            f"{state.instance_ip}:{self.settings.lambda_inference_port}"
        )

    def _extract_chat_content(self, response_data: Dict[str, Any]) -> str:
        """Extract generated text from OpenAI-compatible chat or completion response."""
        choices = response_data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise LLMError("Inference response did not include choices")

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise LLMError("Inference response format is invalid")

        message = first_choice.get("message", {})
        content = message.get("content") if isinstance(message, dict) else None

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            fragments: List[str] = []
            for part in content:
                if isinstance(part, dict):
                    text = part.get("text")
                    if isinstance(text, str) and text:
                        fragments.append(text)
            if fragments:
                return "\n".join(fragments)

        text_value = first_choice.get("text")
        if isinstance(text_value, str):
            return text_value

        raise LLMError("Inference response did not include assistant content")

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert role-based messages into a plain completion prompt."""
        lines: List[str] = []

        for message in messages:
            role = str(message.get("role", "user")).lower().strip()
            content = str(message.get("content", "")).strip()
            if not content:
                continue

            if role == "system":
                lines.append(f"System: {content}")
            elif role == "assistant":
                lines.append(f"Assistant: {content}")
            else:
                lines.append(f"User: {content}")

        lines.append("Assistant:")
        return "\n".join(lines)

    async def _terminate_if_idle_locked(self) -> None:
        """Terminate active instance when idle threshold is exceeded."""
        if not self.settings.lambda_auto_shutdown_enabled:
            return
        if not self._instance_state:
            return
        if not self._instance_state.instance_id:
            return

        idle_seconds = (_utcnow() - self._instance_state.last_used_at).total_seconds()
        if idle_seconds < self.settings.lambda_idle_shutdown_seconds:
            return

        await self._terminate_instance(self._instance_state.instance_id)
        logger.info(
            "lambda_instance_auto_terminated",
            instance_id=self._instance_state.instance_id,
            idle_seconds=idle_seconds,
        )
        self._instance_state = None

    @retry_async(
        max_attempts=3,
        exceptions=(httpx.TimeoutException, httpx.NetworkError),
        base_delay=1.0,
        max_delay=8.0,
    )
    async def _launch_instance(self) -> Dict[str, Any]:
        """Launch a Lambda instance and return API response payload."""
        payload: Dict[str, Any] = {
            "name": self.settings.lambda_instance_name,
            "instance_type_name": self.settings.lambda_instance_type,
            "quantity": 1,
        }

        if self.settings.lambda_region_name:
            payload["region_name"] = self.settings.lambda_region_name

        ssh_key_names = _parse_csv(self.settings.lambda_ssh_key_names)
        if ssh_key_names:
            payload["ssh_key_names"] = ssh_key_names

        file_system_names = _parse_csv(self.settings.lambda_file_system_names)
        if file_system_names:
            payload["file_system_names"] = file_system_names

        response = await self._cloud_client.post(
            self._cloud_url("instance-operations/launch"),
            headers=self._cloud_headers(),
            json=payload,
        )

        if response.status_code >= 400:
            raise APIError(
                f"Lambda launch failed: {response.status_code} - {response.text}",
                code="LAMBDA_LAUNCH_ERROR",
            )

        return response.json()

    async def _fetch_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Fetch instance details from Lambda Cloud API."""
        response = await self._cloud_client.get(
            self._cloud_url("instances"),
            headers=self._cloud_headers(),
        )

        if response.status_code >= 400:
            raise APIError(
                f"Lambda instances query failed: {response.status_code} - {response.text}",
                code="LAMBDA_INSTANCE_QUERY_ERROR",
            )

        payload = response.json()

        for obj in _iter_objects(payload):
            obj_id = obj.get("id") or obj.get("instance_id")
            if isinstance(obj_id, str) and obj_id == instance_id:
                return obj

        return None

    async def _wait_for_instance_ready(self, launch_response: Dict[str, Any]) -> LambdaInstanceState:
        """Wait until launched instance has a reachable IP."""
        instance_id = _extract_first_string(launch_response, ["instance_id", "id", "instance_ids"])
        instance_ip = _extract_first_string(
            launch_response,
            ["ip", "public_ip", "public_ipv4", "ip_address"],
        )

        if instance_id is None and instance_ip:
            return LambdaInstanceState(
                instance_id=None,
                instance_ip=instance_ip,
                status="running",
            )

        if instance_id is None:
            raise APIError("Lambda launch response did not include instance identifier")

        timeout_seconds = max(self.settings.lambda_launch_timeout_seconds, 10)
        poll_interval = max(self.settings.lambda_launch_poll_interval_seconds, 1)
        deadline = time.monotonic() + timeout_seconds

        while time.monotonic() < deadline:
            instance_obj = await self._fetch_instance(instance_id)
            if instance_obj:
                status_value = str(instance_obj.get("status", "")).lower().strip() or None
                instance_ip = _extract_first_string(
                    instance_obj,
                    ["ip", "public_ip", "public_ipv4", "ip_address"],
                )

                if instance_ip and status_value not in {"failed", "error", "terminated"}:
                    return LambdaInstanceState(
                        instance_id=instance_id,
                        instance_ip=instance_ip,
                        status=status_value,
                    )

            await asyncio.sleep(poll_interval)

        raise APIError(
            f"Timed out waiting for Lambda instance {instance_id} to become ready",
            code="LAMBDA_INSTANCE_TIMEOUT",
        )

    async def _ensure_instance_locked(self) -> LambdaInstanceState:
        """Ensure there is a live instance available for inference."""
        if self._instance_state:
            return self._instance_state

        # Fixed external endpoint mode: skip launch lifecycle and call directly.
        if self.settings.lambda_inference_base_url:
            self._instance_state = LambdaInstanceState(
                instance_id=None,
                instance_ip=None,
                status="external_endpoint",
            )
            return self._instance_state

        launch_response = await self._launch_instance()
        self._instance_state = await self._wait_for_instance_ready(launch_response)
        logger.info(
            "lambda_instance_ready",
            instance_id=self._instance_state.instance_id,
            instance_ip=self._instance_state.instance_ip,
        )
        return self._instance_state

    @retry_async(
        max_attempts=3,
        exceptions=(httpx.TimeoutException, httpx.NetworkError),
        base_delay=1.0,
        max_delay=8.0,
    )
    async def _terminate_instance(self, instance_id: str) -> None:
        """Terminate a Lambda instance."""
        payload = {"instance_ids": [instance_id]}
        response = await self._cloud_client.post(
            self._cloud_url("instance-operations/terminate"),
            headers=self._cloud_headers(),
            json=payload,
        )

        if response.status_code >= 400:
            raise APIError(
                f"Lambda terminate failed: {response.status_code} - {response.text}",
                code="LAMBDA_TERMINATE_ERROR",
            )

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> LambdaChatCompletion:
        """Run chat completion via Lambda-hosted model endpoint."""
        if not self.settings.lambda_enabled:
            raise ConfigurationError("Lambda GPU integration is disabled. Set LAMBDA_ENABLED=true.")

        if not messages:
            raise APIError("At least one message is required for inference")

        async with self._instance_lock:
            await self._terminate_if_idle_locked()
            state = await self._ensure_instance_locked()

        inference_base_url = self._resolve_inference_base_url(state)
        endpoint_path = f"/{self.settings.lambda_inference_path.lstrip('/')}"
        endpoint_url = f"{inference_base_url}{endpoint_path}"

        model_name = model or self.settings.lambda_inference_model
        if self.settings.lambda_inference_mode == "completion":
            request_payload = {
                "model": model_name,
                "prompt": self._messages_to_prompt(messages),
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        else:
            request_payload = {
                "model": model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self.settings.lambda_inference_api_key:
            headers["Authorization"] = f"Bearer {self.settings.lambda_inference_api_key}"

        started_at = time.perf_counter()
        response = await self._inference_client.post(
            endpoint_url,
            headers=headers,
            json=request_payload,
        )
        latency_ms = (time.perf_counter() - started_at) * 1000

        if response.status_code >= 400:
            raise APIError(
                f"Lambda inference failed: {response.status_code} - {response.text}",
                code="LAMBDA_INFERENCE_ERROR",
            )

        response_data = response.json()
        content = self._extract_chat_content(response_data)

        async with self._instance_lock:
            if self._instance_state:
                self._instance_state.last_used_at = _utcnow()

        return LambdaChatCompletion(
            content=content,
            model=model_name,
            latency_ms=latency_ms,
            raw_response=response_data,
            instance_id=state.instance_id,
            instance_ip=state.instance_ip,
        )

    async def shutdown_active_instance(self, reason: str = "manual") -> bool:
        """Terminate currently tracked instance, if any."""
        async with self._instance_lock:
            if not self._instance_state or not self._instance_state.instance_id:
                return False

            instance_id = self._instance_state.instance_id
            await self._terminate_instance(instance_id)
            logger.info("lambda_instance_terminated", instance_id=instance_id, reason=reason)
            self._instance_state = None
            return True

    async def close(self) -> None:
        """Close underlying HTTP clients."""
        await self._cloud_client.aclose()
        await self._inference_client.aclose()


_lambda_gpu_service: Optional[LambdaGPUService] = None


def get_lambda_gpu_service() -> LambdaGPUService:
    """Get or create singleton Lambda GPU service."""
    global _lambda_gpu_service
    if _lambda_gpu_service is None:
        _lambda_gpu_service = LambdaGPUService()
    return _lambda_gpu_service


async def close_lambda_gpu_service() -> None:
    """Close singleton Lambda GPU service if initialized."""
    global _lambda_gpu_service
    if _lambda_gpu_service is not None:
        await _lambda_gpu_service.close()
        _lambda_gpu_service = None
