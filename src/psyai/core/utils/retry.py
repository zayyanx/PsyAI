"""
Retry utilities with exponential backoff.

Provides decorators and functions for retrying operations that may fail transiently.
"""

import asyncio
import functools
import random
import time
from typing import Any, Callable, Optional, Tuple, Type, TypeVar, Union

from psyai.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
) -> float:
    """
    Calculate delay using exponential backoff with optional jitter.

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Whether to add random jitter

    Returns:
        Delay in seconds

    Example:
        >>> exponential_backoff(0)  # First retry
        1.0
        >>> exponential_backoff(1)  # Second retry
        2.0
        >>> exponential_backoff(2)  # Third retry
        4.0
    """
    delay = min(base_delay * (exponential_base**attempt), max_delay)

    if jitter:
        # Add random jitter (±25%)
        jitter_range = delay * 0.25
        delay += random.uniform(-jitter_range, jitter_range)

    return max(0, delay)


def retry_sync(
    max_attempts: int = 3,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to retry a synchronous function with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        exceptions: Exception or tuple of exceptions to catch
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Whether to add random jitter
        on_retry: Optional callback function called on each retry

    Returns:
        Decorated function

    Example:
        >>> @retry_sync(max_attempts=3, exceptions=ValueError)
        ... def unreliable_function():
        ...     # Function that might fail
        ...     pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        delay = exponential_backoff(
                            attempt,
                            base_delay=base_delay,
                            max_delay=max_delay,
                            exponential_base=exponential_base,
                            jitter=jitter,
                        )

                        logger.warning(
                            "retry_attempt",
                            function=func.__name__,
                            attempt=attempt + 1,
                            max_attempts=max_attempts,
                            delay=delay,
                            error=str(e),
                        )

                        if on_retry:
                            on_retry(e, attempt)

                        time.sleep(delay)
                    else:
                        logger.error(
                            "retry_failed",
                            function=func.__name__,
                            attempts=max_attempts,
                            error=str(e),
                        )

            # If we get here, all attempts failed
            raise last_exception  # type: ignore

        return wrapper

    return decorator


def retry_async(
    max_attempts: int = 3,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to retry an asynchronous function with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        exceptions: Exception or tuple of exceptions to catch
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Whether to add random jitter
        on_retry: Optional callback function called on each retry

    Returns:
        Decorated async function

    Example:
        >>> @retry_async(max_attempts=3, exceptions=TimeoutError)
        ... async def async_api_call():
        ...     # Async function that might fail
        ...     pass
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        delay = exponential_backoff(
                            attempt,
                            base_delay=base_delay,
                            max_delay=max_delay,
                            exponential_base=exponential_base,
                            jitter=jitter,
                        )

                        logger.warning(
                            "retry_attempt_async",
                            function=func.__name__,
                            attempt=attempt + 1,
                            max_attempts=max_attempts,
                            delay=delay,
                            error=str(e),
                        )

                        if on_retry:
                            on_retry(e, attempt)

                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            "retry_failed_async",
                            function=func.__name__,
                            attempts=max_attempts,
                            error=str(e),
                        )

            # If we get here, all attempts failed
            raise last_exception  # type: ignore

        return wrapper

    return decorator
