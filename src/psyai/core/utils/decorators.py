"""
Useful decorators for PsyAI.

Provides common decorators for timing, caching, and other cross-cutting concerns.
"""

import functools
import time
from typing import Any, Callable, Optional, TypeVar

from psyai.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def timer(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to log execution time of a function.

    Args:
        func: Function to time

    Returns:
        Decorated function

    Example:
        >>> @timer
        ... def slow_function():
        ...     time.sleep(1)
        ...     return "done"
    """

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logger.info(
                "function_execution",
                function=func.__name__,
                duration_seconds=round(duration, 3),
            )

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logger.info(
                "function_execution",
                function=func.__name__,
                duration_seconds=round(duration, 3),
            )

    # Return appropriate wrapper based on function type
    import asyncio

    if asyncio.iscoroutinefunction(func):
        return async_wrapper  # type: ignore
    return sync_wrapper


def log_entry_exit(log_args: bool = False, log_result: bool = False) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to log function entry and exit.

    Args:
        log_args: Whether to log function arguments
        log_result: Whether to log function result

    Returns:
        Decorator function

    Example:
        >>> @log_entry_exit(log_args=True, log_result=True)
        ... def process_data(data: dict):
        ...     return data["value"]
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            log_data = {"function": func.__name__}

            if log_args:
                log_data["args"] = str(args) if args else None
                log_data["kwargs"] = kwargs if kwargs else None

            logger.debug("function_entry", **log_data)

            try:
                result = func(*args, **kwargs)

                if log_result:
                    logger.debug(
                        "function_exit",
                        function=func.__name__,
                        result=str(result) if result is not None else None,
                    )
                else:
                    logger.debug("function_exit", function=func.__name__)

                return result
            except Exception as e:
                logger.error(
                    "function_exception",
                    function=func.__name__,
                    error=str(e),
                )
                raise

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            log_data = {"function": func.__name__}

            if log_args:
                log_data["args"] = str(args) if args else None
                log_data["kwargs"] = kwargs if kwargs else None

            logger.debug("function_entry", **log_data)

            try:
                result = await func(*args, **kwargs)

                if log_result:
                    logger.debug(
                        "function_exit",
                        function=func.__name__,
                        result=str(result) if result is not None else None,
                    )
                else:
                    logger.debug("function_exit", function=func.__name__)

                return result
            except Exception as e:
                logger.error(
                    "function_exception",
                    function=func.__name__,
                    error=str(e),
                )
                raise

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper

    return decorator


def deprecated(reason: str, replacement: Optional[str] = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to mark a function as deprecated.

    Args:
        reason: Reason for deprecation
        replacement: Suggested replacement function

    Returns:
        Decorator function

    Example:
        >>> @deprecated("Use new_function instead", replacement="new_function")
        ... def old_function():
        ...     pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            message = f"Function {func.__name__} is deprecated: {reason}"
            if replacement:
                message += f" Use {replacement} instead."

            logger.warning(
                "deprecated_function_called",
                function=func.__name__,
                reason=reason,
                replacement=replacement,
            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def singleton(cls: type) -> type:
    """
    Decorator to make a class a singleton.

    Args:
        cls: Class to make singleton

    Returns:
        Singleton class

    Example:
        >>> @singleton
        ... class DatabaseConnection:
        ...     pass
    """
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def rate_limit(calls: int, period: int) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Simple rate limiting decorator.

    Args:
        calls: Number of calls allowed
        period: Time period in seconds

    Returns:
        Decorator function

    Example:
        >>> @rate_limit(calls=10, period=60)  # 10 calls per minute
        ... def api_call():
        ...     pass
    """
    from collections import deque
    from time import time

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        call_times: deque = deque(maxlen=calls)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            now = time()

            # Remove old calls outside the period
            while call_times and call_times[0] < now - period:
                call_times.popleft()

            if len(call_times) >= calls:
                sleep_time = period - (now - call_times[0])
                logger.warning(
                    "rate_limit_exceeded",
                    function=func.__name__,
                    sleep_time=sleep_time,
                )
                raise Exception(f"Rate limit exceeded. Try again in {sleep_time:.2f} seconds")

            call_times.append(now)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def memoize(func: Callable[..., T]) -> Callable[..., T]:
    """
    Simple memoization decorator.

    Args:
        func: Function to memoize

    Returns:
        Memoized function

    Example:
        >>> @memoize
        ... def expensive_calculation(n: int) -> int:
        ...     return n ** 2

    Note:
        For production use, consider functools.lru_cache instead
    """
    cache: dict = {}

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        # Create cache key from args and kwargs
        key = str(args) + str(sorted(kwargs.items()))

        if key not in cache:
            cache[key] = func(*args, **kwargs)
            logger.debug(
                "cache_miss",
                function=func.__name__,
                cache_size=len(cache),
            )
        else:
            logger.debug(
                "cache_hit",
                function=func.__name__,
                cache_size=len(cache),
            )

        return cache[key]

    # Add cache management methods
    wrapper.cache_clear = lambda: cache.clear()  # type: ignore
    wrapper.cache_info = lambda: {"size": len(cache), "items": list(cache.keys())}  # type: ignore

    return wrapper
