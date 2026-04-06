"""
Vertex AI client wrapper and configuration.

This module provides a centralized client for interacting with Vertex AI
Gemini models with proper error handling, retry logic, and configuration.
"""

from typing import Any, Dict, List, Optional

import vertexai
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, GenerationConfig, ChatSession

from psyai.core.config import settings
from psyai.core.exceptions import LLMError, LLMRateLimitError, LLMTimeoutError
from psyai.core.logging import get_logger
from psyai.core.utils import retry_async, retry_sync

logger = get_logger(__name__)


class VertexAIClient:
    """
    Wrapper for Vertex AI Gemini models with error handling and retry logic.

    This class provides a centralized interface for interacting with Vertex AI
    Gemini models, with automatic retry, error handling, and logging.

    Example:
        >>> client = VertexAIClient()
        >>> response = await client.agenerate("What is PsyAI?")
        >>> print(response)
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        Initialize Vertex AI client.

        Args:
            model_name: Model name (defaults to settings.vertex_model)
            temperature: Model temperature (defaults to settings.vertex_temperature)
            max_tokens: Max output tokens (defaults to settings.vertex_max_tokens)
            project_id: GCP project ID (defaults to settings.gcp_project_id)
            location: GCP location (defaults to settings.gcp_location)
            **kwargs: Additional arguments passed to GenerationConfig
        """
        self.project_id = project_id or settings.gcp_project_id
        self.location = location or settings.gcp_location
        self.model_name = model_name or settings.vertex_model
        self.temperature = temperature or settings.vertex_temperature
        self.max_tokens = max_tokens or settings.vertex_max_tokens

        if not self.project_id:
            raise ValueError(
                "GCP project_id is required. Set gcp_project_id in config or environment."
            )

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)

        # Create generation config
        self.generation_config = GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            top_p=kwargs.get("top_p", settings.vertex_top_p),
            top_k=kwargs.get("top_k", settings.vertex_top_k),
        )

        # Initialize the model
        self._model = self._create_model()

        logger.info(
            "vertexai_client_initialized",
            project=self.project_id,
            location=self.location,
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    def _create_model(self) -> GenerativeModel:
        """
        Create the Vertex AI model instance.

        Returns:
            GenerativeModel instance

        Raises:
            LLMError: If model creation fails
        """
        try:
            model = GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config,
            )
            return model
        except Exception as e:
            logger.error("vertexai_model_creation_failed", error=str(e))
            raise LLMError(f"Failed to create Vertex AI model: {str(e)}")

    @property
    def model(self) -> GenerativeModel:
        """Get the underlying model instance."""
        return self._model

    def start_chat(self, history: Optional[List[Dict[str, str]]] = None) -> ChatSession:
        """
        Start a chat session.

        Args:
            history: Optional chat history

        Returns:
            ChatSession instance

        Example:
            >>> chat = client.start_chat()
            >>> response = chat.send_message("Hello!")
        """
        return self._model.start_chat(history=history or [])

    @retry_sync(
        max_attempts=3,
        exceptions=(LLMRateLimitError, LLMTimeoutError),
        base_delay=2.0,
    )
    def generate(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        """
        Generate a response synchronously.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation arguments

        Returns:
            Generated response

        Raises:
            LLMError: If generation fails
            LLMRateLimitError: If rate limit is hit
            LLMTimeoutError: If request times out
        """
        try:
            logger.debug("vertexai_generate_start", prompt_length=len(prompt))

            response = self._model.generate_content(
                prompt,
                generation_config=kwargs.get("generation_config", self.generation_config),
            )

            result = response.text

            logger.info(
                "vertexai_generate_complete",
                prompt_length=len(prompt),
                response_length=len(result),
            )

            return result

        except Exception as e:
            error_msg = str(e).lower()

            if "quota" in error_msg or "rate limit" in error_msg or "429" in error_msg:
                logger.warning("vertexai_rate_limit", error=str(e))
                raise LLMRateLimitError(str(e))
            elif "timeout" in error_msg or "timed out" in error_msg:
                logger.warning("vertexai_timeout", error=str(e))
                raise LLMTimeoutError(str(e))
            else:
                logger.error("vertexai_generate_error", error=str(e))
                raise LLMError(f"Vertex AI generation failed: {str(e)}")

    @retry_async(
        max_attempts=3,
        exceptions=(LLMRateLimitError, LLMTimeoutError),
        base_delay=2.0,
    )
    async def agenerate(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> str:
        """
        Generate a response asynchronously.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation arguments

        Returns:
            Generated response

        Raises:
            LLMError: If generation fails
            LLMRateLimitError: If rate limit is hit
            LLMTimeoutError: If request times out
        """
        try:
            logger.debug("vertexai_agenerate_start", prompt_length=len(prompt))

            response = await self._model.generate_content_async(
                prompt,
                generation_config=kwargs.get("generation_config", self.generation_config),
            )

            result = response.text

            logger.info(
                "vertexai_agenerate_complete",
                prompt_length=len(prompt),
                response_length=len(result),
            )

            return result

        except Exception as e:
            error_msg = str(e).lower()

            if "quota" in error_msg or "rate limit" in error_msg or "429" in error_msg:
                logger.warning("vertexai_rate_limit", error=str(e))
                raise LLMRateLimitError(str(e))
            elif "timeout" in error_msg or "timed out" in error_msg:
                logger.warning("vertexai_timeout", error=str(e))
                raise LLMTimeoutError(str(e))
            else:
                logger.error("vertexai_agenerate_error", error=str(e))
                raise LLMError(f"Vertex AI generation failed: {str(e)}")

    def batch_generate(
        self,
        prompts: List[str],
        **kwargs: Any,
    ) -> List[str]:
        """
        Generate responses for multiple prompts in batch.

        Args:
            prompts: List of input prompts
            **kwargs: Additional arguments

        Returns:
            List of generated responses

        Raises:
            LLMError: If batch generation fails
        """
        try:
            logger.info("vertexai_batch_generate_start", batch_size=len(prompts))

            results = []
            for prompt in prompts:
                result = self.generate(prompt, **kwargs)
                results.append(result)

            logger.info(
                "vertexai_batch_generate_complete",
                batch_size=len(prompts),
                results_count=len(results),
            )

            return results

        except Exception as e:
            logger.error("vertexai_batch_generate_error", error=str(e))
            raise LLMError(f"Vertex AI batch generation failed: {str(e)}")

    async def abatch_generate(
        self,
        prompts: List[str],
        **kwargs: Any,
    ) -> List[str]:
        """
        Generate responses for multiple prompts in batch asynchronously.

        Args:
            prompts: List of input prompts
            **kwargs: Additional arguments

        Returns:
            List of generated responses

        Raises:
            LLMError: If batch generation fails
        """
        try:
            logger.info("vertexai_abatch_generate_start", batch_size=len(prompts))

            results = []
            for prompt in prompts:
                result = await self.agenerate(prompt, **kwargs)
                results.append(result)

            logger.info(
                "vertexai_abatch_generate_complete",
                batch_size=len(prompts),
                results_count=len(results),
            )

            return results

        except Exception as e:
            logger.error("vertexai_abatch_generate_error", error=str(e))
            raise LLMError(f"Vertex AI batch generation failed: {str(e)}")

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.

        Args:
            text: Input text

        Returns:
            Number of tokens

        Raises:
            LLMError: If token counting fails
        """
        try:
            result = self._model.count_tokens(text)
            return result.total_tokens
        except Exception as e:
            logger.error("vertexai_token_count_error", error=str(e))
            raise LLMError(f"Token counting failed: {str(e)}")


# Singleton instance
_client: Optional[VertexAIClient] = None


def get_vertexai_client(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    force_new: bool = False,
) -> VertexAIClient:
    """
    Get or create a Vertex AI client instance.

    By default, returns a singleton instance. Set force_new=True to create a new instance.

    Args:
        model_name: Model name (defaults to settings.vertex_model)
        temperature: Model temperature (defaults to settings.vertex_temperature)
        max_tokens: Max tokens (defaults to settings.vertex_max_tokens)
        force_new: Force creation of new instance

    Returns:
        VertexAIClient instance

    Example:
        >>> client = get_vertexai_client()
        >>> response = await client.agenerate("Hello!")
    """
    global _client

    if force_new or _client is None:
        _client = VertexAIClient(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    return _client
