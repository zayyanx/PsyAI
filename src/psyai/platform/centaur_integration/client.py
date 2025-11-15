"""
Centaur Foundation Model client.

This module provides a client for interacting with the Centaur Foundation Model
to predict human decision alignment and confidence scores.
"""

import hashlib
import json
from typing import Any, Dict, List, Optional, Union

import httpx

from psyai.core.config import get_settings
from psyai.core.exceptions import (
    APIError,
    AuthenticationError,
    LLMError,
    RateLimitError,
    ValidationError,
)
from psyai.core.logging import get_logger
from psyai.core.utils.retry import retry_async, retry_sync

logger = get_logger(__name__)
settings = get_settings()


class CentaurClient:
    """
    Client for Centaur Foundation Model.

    The Centaur model specializes in predicting human cognitive patterns
    and decision alignment, helping AI systems better align with human preferences.

    Example:
        >>> client = CentaurClient()
        >>> result = await client.predict_alignment(
        ...     context="User wants to buy a car",
        ...     options=["sedan", "SUV", "truck"],
        ...     user_profile={"age": 35, "family_size": 4}
        ... )
        >>> print(result["predicted_choice"])  # "SUV"
        >>> print(result["confidence"])  # 0.87
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        cache_predictions: bool = True,
    ):
        """
        Initialize Centaur client.

        Args:
            api_key: Centaur API key (defaults to settings)
            base_url: Base URL for Centaur API (defaults to settings)
            timeout: Request timeout in seconds
            cache_predictions: Whether to cache prediction results
        """
        self.api_key = api_key or settings.centaur_api_key
        self.base_url = base_url or settings.centaur_base_url or "https://api.centaur-ai.com/v1"
        self.timeout = timeout or settings.centaur_timeout or 30.0
        self.cache_predictions = cache_predictions

        # Simple in-memory cache for predictions
        self._cache: Dict[str, Dict[str, Any]] = {}

        if not self.api_key:
            logger.warning(
                "centaur_client_no_api_key",
                message="No Centaur API key configured. Set CENTAUR_API_KEY environment variable.",
            )

        # Create HTTP client
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
                "Content-Type": "application/json",
                "User-Agent": f"PsyAI/{settings.app_version}",
            },
        )

        logger.info(
            "centaur_client_initialized",
            base_url=self.base_url,
            cache_enabled=cache_predictions,
        )

    def _get_cache_key(self, data: Dict[str, Any]) -> str:
        """
        Generate cache key from input data.

        Args:
            data: Input data dictionary

        Returns:
            Cache key string
        """
        # Create deterministic hash of input
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def _get_cached_prediction(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get prediction from cache.

        Args:
            cache_key: Cache key

        Returns:
            Cached prediction or None
        """
        if not self.cache_predictions:
            return None

        cached = self._cache.get(cache_key)
        if cached:
            logger.debug("centaur_cache_hit", cache_key=cache_key[:16])
        return cached

    def _cache_prediction(self, cache_key: str, prediction: Dict[str, Any]) -> None:
        """
        Cache a prediction.

        Args:
            cache_key: Cache key
            prediction: Prediction result
        """
        if not self.cache_predictions:
            return

        # Simple size limit: keep only last 1000 predictions
        if len(self._cache) >= 1000:
            # Remove oldest entry (FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[cache_key] = prediction
        logger.debug("centaur_cache_set", cache_key=cache_key[:16])

    def clear_cache(self) -> None:
        """Clear the prediction cache."""
        self._cache.clear()
        logger.info("centaur_cache_cleared")

    @retry_async(
        max_attempts=3,
        exceptions=(httpx.TimeoutException, httpx.NetworkError),
        base_delay=1.0,
        max_delay=10.0,
    )
    async def _make_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Make API request to Centaur.

        Args:
            endpoint: API endpoint
            data: Request data

        Returns:
            Response data

        Raises:
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            ValidationError: Invalid input data
            APIError: Other API errors
        """
        if not self.api_key:
            raise AuthenticationError("Centaur API key not configured")

        try:
            response = await self._client.post(endpoint, json=data)

            # Handle error responses
            if response.status_code == 401:
                raise AuthenticationError("Invalid Centaur API key")
            elif response.status_code == 429:
                raise RateLimitError("Centaur API rate limit exceeded")
            elif response.status_code == 422:
                raise ValidationError(f"Invalid request data: {response.text}")
            elif response.status_code >= 400:
                raise APIError(
                    f"Centaur API error: {response.status_code} - {response.text}",
                    code="CENTAUR_API_ERROR",
                )

            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException as e:
            logger.error("centaur_request_timeout", endpoint=endpoint)
            raise LLMError(f"Centaur request timed out: {endpoint}") from e
        except httpx.NetworkError as e:
            logger.error("centaur_network_error", endpoint=endpoint, error=str(e))
            raise APIError(f"Network error: {str(e)}") from e
        except Exception as e:
            if isinstance(e, (AuthenticationError, RateLimitError, ValidationError, APIError, LLMError)):
                raise
            logger.error("centaur_unexpected_error", error=str(e))
            raise APIError(f"Unexpected error: {str(e)}") from e

    async def predict_alignment(
        self,
        context: str,
        options: List[str],
        user_profile: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Predict which option best aligns with human decision-making.

        Args:
            context: Decision context or scenario
            options: List of possible choices/options
            user_profile: Optional user profile (demographics, preferences, etc.)
            metadata: Optional metadata for tracking

        Returns:
            Dictionary containing:
                - predicted_choice: The predicted option
                - confidence: Confidence score (0.0 to 1.0)
                - reasoning: Explanation of prediction
                - option_scores: Scores for all options

        Example:
            >>> result = await client.predict_alignment(
            ...     context="Customer needs a laptop for gaming",
            ...     options=["MacBook Pro", "Gaming Laptop", "Chromebook"],
            ...     user_profile={"age": 25, "interests": ["gaming", "tech"]}
            ... )
            >>> print(result["predicted_choice"])  # "Gaming Laptop"
        """
        if not options:
            raise ValidationError("At least one option must be provided")

        if len(options) > 20:
            raise ValidationError("Maximum 20 options allowed")

        # Prepare request data
        request_data = {
            "context": context,
            "options": options,
            "user_profile": user_profile or {},
            "metadata": metadata or {},
        }

        # Check cache
        cache_key = self._get_cache_key(request_data)
        cached = self._get_cached_prediction(cache_key)
        if cached:
            return cached

        logger.info(
            "centaur_predict_alignment",
            context_length=len(context),
            num_options=len(options),
            has_profile=user_profile is not None,
        )

        # Make API request
        try:
            response = await self._make_request("/predict/alignment", request_data)

            result = {
                "predicted_choice": response.get("predicted_choice"),
                "confidence": response.get("confidence", 0.0),
                "reasoning": response.get("reasoning", ""),
                "option_scores": response.get("option_scores", {}),
                "metadata": response.get("metadata", {}),
            }

            # Cache result
            self._cache_prediction(cache_key, result)

            logger.info(
                "centaur_alignment_predicted",
                choice=result["predicted_choice"],
                confidence=result["confidence"],
            )

            return result

        except Exception as e:
            logger.error("centaur_predict_alignment_failed", error=str(e))
            raise

    async def calculate_confidence_score(
        self,
        ai_response: str,
        context: str,
        user_feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate confidence score for an AI response.

        Predicts how likely a human would agree with or accept the AI's response.

        Args:
            ai_response: The AI-generated response
            context: Context/prompt that led to the response
            user_feedback: Optional user feedback on the response

        Returns:
            Dictionary containing:
                - confidence_score: Overall confidence (0.0 to 1.0)
                - dimensions: Breakdown by dimension (accuracy, relevance, clarity)
                - explanation: Explanation of the score
                - suggestions: Suggestions for improvement

        Example:
            >>> result = await client.calculate_confidence_score(
            ...     ai_response="Python is the best language for data science",
            ...     context="What's the best programming language for ML?"
            ... )
            >>> print(result["confidence_score"])  # 0.85
        """
        request_data = {
            "ai_response": ai_response,
            "context": context,
            "user_feedback": user_feedback,
        }

        # Check cache
        cache_key = self._get_cache_key(request_data)
        cached = self._get_cached_prediction(cache_key)
        if cached:
            return cached

        logger.info(
            "centaur_calculate_confidence",
            response_length=len(ai_response),
            context_length=len(context),
            has_feedback=user_feedback is not None,
        )

        try:
            response = await self._make_request("/predict/confidence", request_data)

            result = {
                "confidence_score": response.get("confidence_score", 0.0),
                "dimensions": response.get("dimensions", {}),
                "explanation": response.get("explanation", ""),
                "suggestions": response.get("suggestions", []),
                "metadata": response.get("metadata", {}),
            }

            # Cache result
            self._cache_prediction(cache_key, result)

            logger.info(
                "centaur_confidence_calculated",
                score=result["confidence_score"],
            )

            return result

        except Exception as e:
            logger.error("centaur_calculate_confidence_failed", error=str(e))
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
        logger.info("centaur_client_closed")

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()


# Singleton instance
_centaur_client: Optional[CentaurClient] = None


def get_centaur_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs,
) -> CentaurClient:
    """
    Get or create singleton Centaur client.

    Args:
        api_key: Optional API key override
        base_url: Optional base URL override
        **kwargs: Additional client options

    Returns:
        CentaurClient instance

    Example:
        >>> client = get_centaur_client()
        >>> result = await client.predict_alignment(...)
    """
    global _centaur_client

    if _centaur_client is None:
        _centaur_client = CentaurClient(
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )

    return _centaur_client
