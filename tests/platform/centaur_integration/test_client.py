"""Tests for Centaur client."""

import hashlib
import json
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest

from psyai.core.exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)
from psyai.platform.centaur_integration.client import (
    CentaurClient,
    get_centaur_client,
)


@pytest.fixture
def mock_settings():
    """Mock settings."""
    with patch("psyai.platform.centaur_integration.client.settings") as mock:
        mock.centaur_api_key = "test-api-key"
        mock.centaur_base_url = "https://api.test.com/v1"
        mock.centaur_timeout = 30.0
        mock.app_version = "0.1.0"
        yield mock


@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient."""
    with patch("psyai.platform.centaur_integration.client.httpx.AsyncClient") as mock:
        client_instance = AsyncMock()
        mock.return_value = client_instance
        yield client_instance


class TestCentaurClient:
    """Test CentaurClient."""

    def test_initialization(self, mock_settings):
        """Test client initialization."""
        client = CentaurClient(
            api_key="custom-key",
            base_url="https://custom.com",
            timeout=60.0,
            cache_predictions=True,
        )

        assert client.api_key == "custom-key"
        assert client.base_url == "https://custom.com"
        assert client.timeout == 60.0
        assert client.cache_predictions is True
        assert isinstance(client._cache, dict)

    def test_initialization_with_defaults(self, mock_settings):
        """Test initialization with default values from settings."""
        client = CentaurClient()

        assert client.api_key == "test-api-key"
        assert client.base_url == "https://api.test.com/v1"
        assert client.timeout == 30.0

    def test_cache_key_generation(self, mock_settings):
        """Test cache key generation."""
        client = CentaurClient()

        data = {"context": "test", "options": ["a", "b"]}
        key1 = client._get_cache_key(data)
        key2 = client._get_cache_key(data)

        # Same data should produce same key
        assert key1 == key2

        # Different data should produce different key
        data2 = {"context": "test", "options": ["a", "c"]}
        key3 = client._get_cache_key(data2)
        assert key1 != key3

        # Key should be deterministic hash
        expected = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        assert key1 == expected

    def test_cache_operations(self, mock_settings):
        """Test cache get/set operations."""
        client = CentaurClient()

        # Cache miss
        assert client._get_cached_prediction("nonexistent") is None

        # Cache hit
        prediction = {"predicted_choice": "a", "confidence": 0.9}
        client._cache_prediction("key1", prediction)
        assert client._get_cached_prediction("key1") == prediction

        # Cache clearing
        client.clear_cache()
        assert client._get_cached_prediction("key1") is None

    def test_cache_size_limit(self, mock_settings):
        """Test cache size limit (FIFO eviction)."""
        client = CentaurClient()

        # Add 1001 items (exceeds 1000 limit)
        for i in range(1001):
            client._cache_prediction(f"key_{i}", {"data": i})

        # First item should be evicted
        assert client._get_cached_prediction("key_0") is None
        # Last item should still be there
        assert client._get_cached_prediction("key_1000") is not None
        # Cache size should be 1000
        assert len(client._cache) == 1000

    def test_caching_disabled(self, mock_settings):
        """Test when caching is disabled."""
        client = CentaurClient(cache_predictions=False)

        prediction = {"predicted_choice": "a"}
        client._cache_prediction("key1", prediction)
        assert client._get_cached_prediction("key1") is None

    @pytest.mark.asyncio
    async def test_make_request_success(self, mock_settings, mock_httpx_client):
        """Test successful API request."""
        client = CentaurClient()

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_httpx_client.post = AsyncMock(return_value=mock_response)

        result = await client._make_request("/test", {"data": "test"})

        assert result == {"result": "success"}
        mock_httpx_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_authentication_error(self, mock_settings, mock_httpx_client):
        """Test authentication error handling."""
        client = CentaurClient()

        mock_response = Mock()
        mock_response.status_code = 401
        mock_httpx_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(AuthenticationError, match="Invalid Centaur API key"):
            await client._make_request("/test", {"data": "test"})

    @pytest.mark.asyncio
    async def test_make_request_rate_limit_error(self, mock_settings, mock_httpx_client):
        """Test rate limit error handling."""
        client = CentaurClient()

        mock_response = Mock()
        mock_response.status_code = 429
        mock_httpx_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(RateLimitError, match="rate limit exceeded"):
            await client._make_request("/test", {"data": "test"})

    @pytest.mark.asyncio
    async def test_make_request_validation_error(self, mock_settings, mock_httpx_client):
        """Test validation error handling."""
        client = CentaurClient()

        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.text = "Invalid data"
        mock_httpx_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(ValidationError, match="Invalid request data"):
            await client._make_request("/test", {"data": "test"})

    @pytest.mark.asyncio
    async def test_make_request_api_error(self, mock_settings, mock_httpx_client):
        """Test generic API error handling."""
        client = CentaurClient()

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_httpx_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(APIError, match="Centaur API error"):
            await client._make_request("/test", {"data": "test"})

    @pytest.mark.asyncio
    async def test_make_request_no_api_key(self, mock_settings):
        """Test request without API key."""
        client = CentaurClient(api_key=None)

        with pytest.raises(AuthenticationError, match="API key not configured"):
            await client._make_request("/test", {"data": "test"})

    @pytest.mark.asyncio
    async def test_predict_alignment_success(self, mock_settings, mock_httpx_client):
        """Test successful alignment prediction."""
        client = CentaurClient()

        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "predicted_choice": "option_a",
            "confidence": 0.85,
            "reasoning": "Best fit based on profile",
            "option_scores": {"option_a": 0.85, "option_b": 0.60},
            "metadata": {},
        }
        mock_httpx_client.post = AsyncMock(return_value=mock_response)

        result = await client.predict_alignment(
            context="Choose option",
            options=["option_a", "option_b"],
            user_profile={"age": 30},
        )

        assert result["predicted_choice"] == "option_a"
        assert result["confidence"] == 0.85
        assert "option_scores" in result

    @pytest.mark.asyncio
    async def test_predict_alignment_with_cache(self, mock_settings, mock_httpx_client):
        """Test alignment prediction with caching."""
        client = CentaurClient()

        # First call - cache miss
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "predicted_choice": "option_a",
            "confidence": 0.85,
            "reasoning": "Test",
            "option_scores": {},
            "metadata": {},
        }
        mock_httpx_client.post = AsyncMock(return_value=mock_response)

        result1 = await client.predict_alignment(
            context="test",
            options=["option_a", "option_b"],
        )

        # Second call with same inputs - should use cache
        result2 = await client.predict_alignment(
            context="test",
            options=["option_a", "option_b"],
        )

        # Should only call API once
        assert mock_httpx_client.post.call_count == 1
        assert result1 == result2

    @pytest.mark.asyncio
    async def test_predict_alignment_validation_errors(self, mock_settings):
        """Test alignment prediction validation."""
        client = CentaurClient()

        # Empty options
        with pytest.raises(ValidationError, match="At least one option"):
            await client.predict_alignment(context="test", options=[])

        # Too many options
        with pytest.raises(ValidationError, match="Maximum 20 options"):
            await client.predict_alignment(
                context="test",
                options=[f"option_{i}" for i in range(21)],
            )

    @pytest.mark.asyncio
    async def test_calculate_confidence_score_success(self, mock_settings, mock_httpx_client):
        """Test successful confidence calculation."""
        client = CentaurClient()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "confidence_score": 0.92,
            "dimensions": {"accuracy": 0.95, "relevance": 0.90},
            "explanation": "High quality response",
            "suggestions": ["Add more detail"],
            "metadata": {},
        }
        mock_httpx_client.post = AsyncMock(return_value=mock_response)

        result = await client.calculate_confidence_score(
            ai_response="Test response",
            context="Test context",
        )

        assert result["confidence_score"] == 0.92
        assert "dimensions" in result
        assert "suggestions" in result

    @pytest.mark.asyncio
    async def test_calculate_confidence_with_cache(self, mock_settings, mock_httpx_client):
        """Test confidence calculation with caching."""
        client = CentaurClient()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "confidence_score": 0.85,
            "dimensions": {},
            "explanation": "Test",
            "suggestions": [],
            "metadata": {},
        }
        mock_httpx_client.post = AsyncMock(return_value=mock_response)

        # First call
        result1 = await client.calculate_confidence_score(
            ai_response="Test",
            context="Context",
        )

        # Second call with same inputs
        result2 = await client.calculate_confidence_score(
            ai_response="Test",
            context="Context",
        )

        # Should only call API once
        assert mock_httpx_client.post.call_count == 1
        assert result1 == result2

    @pytest.mark.asyncio
    async def test_close(self, mock_settings, mock_httpx_client):
        """Test client close."""
        client = CentaurClient()
        await client.close()

        mock_httpx_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_settings, mock_httpx_client):
        """Test client as context manager."""
        async with CentaurClient() as client:
            assert isinstance(client, CentaurClient)

        mock_httpx_client.aclose.assert_called_once()


def test_get_centaur_client_singleton(mock_settings):
    """Test singleton client creation."""
    # Reset singleton
    import psyai.platform.centaur_integration.client as client_module
    client_module._centaur_client = None

    client1 = get_centaur_client()
    client2 = get_centaur_client()

    assert client1 is client2

    # Cleanup
    client_module._centaur_client = None
