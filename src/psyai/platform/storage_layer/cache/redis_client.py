"""
Redis cache client.

This module provides a Redis client for caching and session storage.
"""

import json
from typing import Any, List, Optional, Union

import redis
from redis.asyncio import Redis as AsyncRedis

from psyai.core.config import get_settings
from psyai.core.exceptions import CacheError
from psyai.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class RedisClient:
    """
    Redis client for caching and session storage.

    Supports both sync and async operations.

    Example:
        >>> client = RedisClient()
        >>> client.set("key", {"data": "value"})
        >>> result = client.get("key")
        >>> print(result)  # {"data": "value"}
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        password: Optional[str] = None,
        decode_responses: bool = True,
    ):
        """
        Initialize Redis client.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            decode_responses: Whether to decode byte responses to strings
        """
        self.host = host or settings.redis_host or "localhost"
        self.port = port or settings.redis_port or 6379
        self.db = db or settings.redis_db or 0
        self.password = password or settings.redis_password
        self.decode_responses = decode_responses

        self._sync_client: Optional[redis.Redis] = None
        self._async_client: Optional[AsyncRedis] = None

        logger.info(
            "redis_client_initialized",
            host=self.host,
            port=self.port,
            db=self.db,
        )

    @property
    def sync_client(self) -> redis.Redis:
        """Get or create sync Redis client."""
        if self._sync_client is None:
            self._sync_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
            )
            logger.debug("sync_redis_client_created")

        return self._sync_client

    @property
    def async_client(self) -> AsyncRedis:
        """Get or create async Redis client."""
        if self._async_client is None:
            self._async_client = AsyncRedis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
            )
            logger.debug("async_redis_client_created")

        return self._async_client

    def _serialize(self, value: Any) -> str:
        """
        Serialize value to JSON string.

        Args:
            value: Value to serialize

        Returns:
            JSON string
        """
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        return json.dumps(value)

    def _deserialize(self, value: Optional[str]) -> Any:
        """
        Deserialize JSON string to value.

        Args:
            value: JSON string

        Returns:
            Deserialized value
        """
        if value is None:
            return None

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # If it's not JSON, return as-is
            return value

    # Synchronous methods

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set a key-value pair.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds

        Returns:
            True if successful

        Raises:
            CacheError: If operation fails
        """
        try:
            serialized = self._serialize(value)
            result = self.sync_client.set(key, serialized, ex=ttl)
            logger.debug("cache_set", key=key, ttl=ttl)
            return bool(result)
        except Exception as e:
            logger.error("cache_set_error", key=key, error=str(e))
            raise CacheError(f"Failed to set cache key: {key}") from e

    def get(self, key: str) -> Optional[Any]:
        """
        Get value by key.

        Args:
            key: Cache key

        Returns:
            Cached value or None

        Raises:
            CacheError: If operation fails
        """
        try:
            value = self.sync_client.get(key)
            if value is not None:
                logger.debug("cache_hit", key=key)
                return self._deserialize(value)
            else:
                logger.debug("cache_miss", key=key)
                return None
        except Exception as e:
            logger.error("cache_get_error", key=key, error=str(e))
            raise CacheError(f"Failed to get cache key: {key}") from e

    def delete(self, *keys: str) -> int:
        """
        Delete one or more keys.

        Args:
            *keys: Keys to delete

        Returns:
            Number of keys deleted

        Raises:
            CacheError: If operation fails
        """
        try:
            count = self.sync_client.delete(*keys)
            logger.debug("cache_delete", keys=keys, count=count)
            return count
        except Exception as e:
            logger.error("cache_delete_error", keys=keys, error=str(e))
            raise CacheError(f"Failed to delete cache keys") from e

    def exists(self, *keys: str) -> int:
        """
        Check if keys exist.

        Args:
            *keys: Keys to check

        Returns:
            Number of existing keys

        Raises:
            CacheError: If operation fails
        """
        try:
            count = self.sync_client.exists(*keys)
            return count
        except Exception as e:
            logger.error("cache_exists_error", keys=keys, error=str(e))
            raise CacheError(f"Failed to check cache keys") from e

    def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for a key.

        Args:
            key: Cache key
            ttl: Time to live in seconds

        Returns:
            True if successful

        Raises:
            CacheError: If operation fails
        """
        try:
            result = self.sync_client.expire(key, ttl)
            logger.debug("cache_expire", key=key, ttl=ttl)
            return bool(result)
        except Exception as e:
            logger.error("cache_expire_error", key=key, error=str(e))
            raise CacheError(f"Failed to set expiration for key: {key}") from e

    def keys(self, pattern: str = "*") -> List[str]:
        """
        Find keys matching pattern.

        Args:
            pattern: Key pattern (supports wildcards)

        Returns:
            List of matching keys

        Raises:
            CacheError: If operation fails
        """
        try:
            keys = self.sync_client.keys(pattern)
            return [k.decode() if isinstance(k, bytes) else k for k in keys]
        except Exception as e:
            logger.error("cache_keys_error", pattern=pattern, error=str(e))
            raise CacheError(f"Failed to get keys with pattern: {pattern}") from e

    def flush(self) -> bool:
        """
        Clear all keys in the current database.

        WARNING: This deletes all data in the database!

        Returns:
            True if successful

        Raises:
            CacheError: If operation fails
        """
        try:
            if settings.app_env == "production":
                raise CacheError("Cannot flush cache in production!")

            result = self.sync_client.flushdb()
            logger.warning("cache_flushed")
            return bool(result)
        except Exception as e:
            logger.error("cache_flush_error", error=str(e))
            raise CacheError("Failed to flush cache") from e

    def ping(self) -> bool:
        """
        Check if Redis is available.

        Returns:
            True if Redis is available

        Raises:
            CacheError: If Redis is not available
        """
        try:
            return self.sync_client.ping()
        except Exception as e:
            logger.error("redis_ping_error", error=str(e))
            raise CacheError("Redis is not available") from e

    # Asynchronous methods

    async def aset(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Async: Set a key-value pair.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        try:
            serialized = self._serialize(value)
            result = await self.async_client.set(key, serialized, ex=ttl)
            logger.debug("async_cache_set", key=key, ttl=ttl)
            return bool(result)
        except Exception as e:
            logger.error("async_cache_set_error", key=key, error=str(e))
            raise CacheError(f"Failed to set cache key: {key}") from e

    async def aget(self, key: str) -> Optional[Any]:
        """
        Async: Get value by key.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            value = await self.async_client.get(key)
            if value is not None:
                logger.debug("async_cache_hit", key=key)
                return self._deserialize(value)
            else:
                logger.debug("async_cache_miss", key=key)
                return None
        except Exception as e:
            logger.error("async_cache_get_error", key=key, error=str(e))
            raise CacheError(f"Failed to get cache key: {key}") from e

    async def adelete(self, *keys: str) -> int:
        """
        Async: Delete one or more keys.

        Args:
            *keys: Keys to delete

        Returns:
            Number of keys deleted
        """
        try:
            count = await self.async_client.delete(*keys)
            logger.debug("async_cache_delete", keys=keys, count=count)
            return count
        except Exception as e:
            logger.error("async_cache_delete_error", keys=keys, error=str(e))
            raise CacheError(f"Failed to delete cache keys") from e

    async def aclose(self) -> None:
        """Close async Redis connection."""
        if self._async_client:
            await self._async_client.close()
            logger.debug("async_redis_client_closed")

    def close(self) -> None:
        """Close sync Redis connection."""
        if self._sync_client:
            self._sync_client.close()
            logger.debug("sync_redis_client_closed")


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """
    Get or create global Redis client.

    Returns:
        RedisClient instance
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = RedisClient()

    return _redis_client
