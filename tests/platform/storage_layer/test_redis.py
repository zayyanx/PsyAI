"""Tests for Redis client."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from psyai.core.exceptions import CacheError
from psyai.platform.storage_layer.cache.redis_client import RedisClient, get_redis_client


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch("psyai.platform.storage_layer.cache.redis_client.redis.Redis") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_async_redis():
    """Mock async Redis client."""
    with patch("psyai.platform.storage_layer.cache.redis_client.AsyncRedis") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


class TestRedisClient:
    """Test RedisClient."""

    def test_initialization(self):
        """Test client initialization."""
        client = RedisClient(
            host="localhost",
            port=6379,
            db=0,
            password="secret",
        )

        assert client.host == "localhost"
        assert client.port == 6379
        assert client.db == 0
        assert client.password == "secret"

    def test_initialization_with_defaults(self):
        """Test initialization with default values."""
        with patch("psyai.platform.storage_layer.cache.redis_client.settings") as mock_settings:
            mock_settings.redis_host = "redis.example.com"
            mock_settings.redis_port = 6380
            mock_settings.redis_db = 1
            mock_settings.redis_password = "pass"

            client = RedisClient()

            assert client.host == "redis.example.com"
            assert client.port == 6380
            assert client.db == 1
            assert client.password == "pass"

    def test_serialize_primitives(self):
        """Test serialization of primitive types."""
        client = RedisClient()

        assert client._serialize("hello") == "hello"
        assert client._serialize(42) == "42"
        assert client._serialize(3.14) == "3.14"
        assert client._serialize(True) == "True"

    def test_serialize_dict(self):
        """Test serialization of dictionary."""
        client = RedisClient()

        result = client._serialize({"key": "value", "number": 42})
        assert '"key"' in result
        assert '"value"' in result
        assert '"number"' in result

    def test_deserialize_json(self):
        """Test deserialization of JSON."""
        client = RedisClient()

        result = client._deserialize('{"key": "value"}')
        assert result == {"key": "value"}

    def test_deserialize_non_json(self):
        """Test deserialization of non-JSON strings."""
        client = RedisClient()

        assert client._deserialize("hello") == "hello"
        assert client._deserialize(None) is None

    def test_set(self, mock_redis):
        """Test set operation."""
        mock_redis.set.return_value = True

        client = RedisClient()
        result = client.set("key", "value", ttl=3600)

        assert result is True
        mock_redis.set.assert_called_once()
        args = mock_redis.set.call_args
        assert args[0][0] == "key"
        assert args[0][1] == "value"
        assert args[1]["ex"] == 3600

    def test_set_dict(self, mock_redis):
        """Test set operation with dict value."""
        mock_redis.set.return_value = True

        client = RedisClient()
        result = client.set("key", {"data": "value"})

        assert result is True
        mock_redis.set.assert_called_once()

    def test_set_error(self, mock_redis):
        """Test set operation error."""
        mock_redis.set.side_effect = Exception("Connection error")

        client = RedisClient()

        with pytest.raises(CacheError, match="Failed to set cache key"):
            client.set("key", "value")

    def test_get(self, mock_redis):
        """Test get operation."""
        mock_redis.get.return_value = "value"

        client = RedisClient()
        result = client.get("key")

        assert result == "value"
        mock_redis.get.assert_called_once_with("key")

    def test_get_json(self, mock_redis):
        """Test get operation with JSON value."""
        mock_redis.get.return_value = '{"data": "value"}'

        client = RedisClient()
        result = client.get("key")

        assert result == {"data": "value"}

    def test_get_none(self, mock_redis):
        """Test get operation with non-existent key."""
        mock_redis.get.return_value = None

        client = RedisClient()
        result = client.get("key")

        assert result is None

    def test_get_error(self, mock_redis):
        """Test get operation error."""
        mock_redis.get.side_effect = Exception("Connection error")

        client = RedisClient()

        with pytest.raises(CacheError, match="Failed to get cache key"):
            client.get("key")

    def test_delete(self, mock_redis):
        """Test delete operation."""
        mock_redis.delete.return_value = 2

        client = RedisClient()
        result = client.delete("key1", "key2")

        assert result == 2
        mock_redis.delete.assert_called_once_with("key1", "key2")

    def test_delete_error(self, mock_redis):
        """Test delete operation error."""
        mock_redis.delete.side_effect = Exception("Connection error")

        client = RedisClient()

        with pytest.raises(CacheError, match="Failed to delete cache keys"):
            client.delete("key")

    def test_exists(self, mock_redis):
        """Test exists operation."""
        mock_redis.exists.return_value = 1

        client = RedisClient()
        result = client.exists("key")

        assert result == 1
        mock_redis.exists.assert_called_once_with("key")

    def test_expire(self, mock_redis):
        """Test expire operation."""
        mock_redis.expire.return_value = True

        client = RedisClient()
        result = client.expire("key", 3600)

        assert result is True
        mock_redis.expire.assert_called_once_with("key", 3600)

    def test_keys(self, mock_redis):
        """Test keys operation."""
        mock_redis.keys.return_value = [b"key1", b"key2"]

        client = RedisClient()
        result = client.keys("test:*")

        assert result == ["key1", "key2"]
        mock_redis.keys.assert_called_once_with("test:*")

    def test_flush(self, mock_redis):
        """Test flush operation."""
        mock_redis.flushdb.return_value = True

        with patch("psyai.platform.storage_layer.cache.redis_client.settings") as mock_settings:
            mock_settings.app_env = "development"

            client = RedisClient()
            result = client.flush()

            assert result is True
            mock_redis.flushdb.assert_called_once()

    def test_flush_production_error(self, mock_redis):
        """Test flush operation in production."""
        with patch("psyai.platform.storage_layer.cache.redis_client.settings") as mock_settings:
            mock_settings.app_env = "production"

            client = RedisClient()

            with pytest.raises(CacheError, match="Cannot flush cache in production"):
                client.flush()

    def test_ping(self, mock_redis):
        """Test ping operation."""
        mock_redis.ping.return_value = True

        client = RedisClient()
        result = client.ping()

        assert result is True
        mock_redis.ping.assert_called_once()

    def test_ping_error(self, mock_redis):
        """Test ping operation error."""
        mock_redis.ping.side_effect = Exception("Connection refused")

        client = RedisClient()

        with pytest.raises(CacheError, match="Redis is not available"):
            client.ping()

    @pytest.mark.asyncio
    async def test_aset(self, mock_async_redis):
        """Test async set operation."""
        mock_async_redis.set.return_value = True

        client = RedisClient()
        result = await client.aset("key", "value", ttl=3600)

        assert result is True
        mock_async_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_aget(self, mock_async_redis):
        """Test async get operation."""
        mock_async_redis.get.return_value = "value"

        client = RedisClient()
        result = await client.aget("key")

        assert result == "value"
        mock_async_redis.get.assert_called_once_with("key")

    @pytest.mark.asyncio
    async def test_adelete(self, mock_async_redis):
        """Test async delete operation."""
        mock_async_redis.delete.return_value = 1

        client = RedisClient()
        result = await client.adelete("key")

        assert result == 1
        mock_async_redis.delete.assert_called_once_with("key")

    @pytest.mark.asyncio
    async def test_aclose(self, mock_async_redis):
        """Test async close operation."""
        client = RedisClient()
        await client.aclose()

        mock_async_redis.close.assert_called_once()

    def test_close(self, mock_redis):
        """Test close operation."""
        client = RedisClient()
        client.close()

        mock_redis.close.assert_called_once()


def test_get_redis_client_singleton():
    """Test singleton client creation."""
    # Reset singleton
    import psyai.platform.storage_layer.cache.redis_client as client_module
    client_module._redis_client = None

    client1 = get_redis_client()
    client2 = get_redis_client()

    assert client1 is client2

    # Cleanup
    client_module._redis_client = None
