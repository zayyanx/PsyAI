"""
Tracing decorators for automatic instrumentation.

This module provides decorators to automatically trace function calls
and send them to LangSmith for observability.
"""

import functools
import time
from typing import Any, Callable, Dict, Optional, TypeVar

from psyai.core.config import settings
from psyai.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def trace(
    name: Optional[str] = None,
    project_name: Optional[str] = None,
    tags: Optional[list] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to trace function execution with LangSmith.

    Args:
        name: Name for the trace (defaults to function name)
        project_name: Project name (defaults to settings)
        tags: Optional tags for the trace
        metadata: Optional metadata

    Returns:
        Decorated function

    Example:
        >>> @trace(name="chat_handler", tags=["production"])
        ... async def handle_chat(message: str) -> str:
        ...     return f"Response to: {message}"
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        trace_name = name or func.__name__
        proj_name = project_name or settings.langsmith_project

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            if not settings.langsmith_tracing:
                return func(*args, **kwargs)

            start_time = time.time()

            # Prepare inputs
            inputs = {
                "args": str(args) if args else None,
                "kwargs": kwargs if kwargs else None,
            }

            try:
                logger.debug(
                    "trace_start",
                    name=trace_name,
                    project=proj_name,
                )

                result = func(*args, **kwargs)

                # Log successful trace
                duration = time.time() - start_time
                logger.info(
                    "trace_complete",
                    name=trace_name,
                    duration=duration,
                    tags=tags,
                )

                return result

            except Exception as e:
                # Log failed trace
                duration = time.time() - start_time
                logger.error(
                    "trace_error",
                    name=trace_name,
                    duration=duration,
                    error=str(e),
                )
                raise

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            if not settings.langsmith_tracing:
                return await func(*args, **kwargs)

            start_time = time.time()

            # Prepare inputs
            inputs = {
                "args": str(args) if args else None,
                "kwargs": kwargs if kwargs else None,
            }

            try:
                logger.debug(
                    "trace_start_async",
                    name=trace_name,
                    project=proj_name,
                )

                result = await func(*args, **kwargs)

                # Log successful trace
                duration = time.time() - start_time
                logger.info(
                    "trace_complete_async",
                    name=trace_name,
                    duration=duration,
                    tags=tags,
                )

                return result

            except Exception as e:
                # Log failed trace
                duration = time.time() - start_time
                logger.error(
                    "trace_error_async",
                    name=trace_name,
                    duration=duration,
                    error=str(e),
                )
                raise

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper

    return decorator


def trace_chain(
    name: Optional[str] = None,
    project_name: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator specifically for tracing LangChain chains.

    This is a convenience wrapper around @trace with chain-specific defaults.

    Args:
        name: Name for the trace (defaults to function name)
        project_name: Project name (defaults to settings)

    Returns:
        Decorated function

    Example:
        >>> @trace_chain(name="conversational_chain")
        ... async def create_chat_chain() -> Chain:
        ...     return ConversationChain(...)
    """
    return trace(
        name=name,
        project_name=project_name,
        tags=["chain"],
    )


def trace_agent(
    name: Optional[str] = None,
    project_name: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator specifically for tracing agent executions.

    This is a convenience wrapper around @trace with agent-specific defaults.

    Args:
        name: Name for the trace (defaults to function name)
        project_name: Project name (defaults to settings)

    Returns:
        Decorated function

    Example:
        >>> @trace_agent(name="decision_agent")
        ... async def run_agent(query: str) -> str:
        ...     return agent.run(query)
    """
    return trace(
        name=name,
        project_name=project_name,
        tags=["agent"],
    )


def trace_llm_call(
    name: Optional[str] = None,
    project_name: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator specifically for tracing LLM API calls.

    This is a convenience wrapper around @trace with LLM-specific defaults.

    Args:
        name: Name for the trace (defaults to function name)
        project_name: Project name (defaults to settings)

    Returns:
        Decorated function

    Example:
        >>> @trace_llm_call(name="openai_completion")
        ... async def get_completion(prompt: str) -> str:
        ...     return await llm.agenerate(prompt)
    """
    return trace(
        name=name,
        project_name=project_name,
        tags=["llm"],
    )


class TraceContext:
    """
    Context manager for tracing code blocks.

    Example:
        >>> with TraceContext("data_processing"):
        ...     # Your code here
        ...     result = process_data()
        >>> print("Processing traced!")
    """

    def __init__(
        self,
        name: str,
        project_name: Optional[str] = None,
        tags: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize trace context.

        Args:
            name: Name for the trace
            project_name: Project name (defaults to settings)
            tags: Optional tags
            metadata: Optional metadata
        """
        self.name = name
        self.project_name = project_name or settings.langsmith_project
        self.tags = tags or []
        self.metadata = metadata or {}
        self.start_time: Optional[float] = None

    def __enter__(self) -> "TraceContext":
        """Enter the trace context."""
        if not settings.langsmith_tracing:
            return self

        self.start_time = time.time()

        logger.debug(
            "trace_context_start",
            name=self.name,
            project=self.project_name,
        )

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the trace context."""
        if not settings.langsmith_tracing or self.start_time is None:
            return

        duration = time.time() - self.start_time

        if exc_type is None:
            logger.info(
                "trace_context_complete",
                name=self.name,
                duration=duration,
                tags=self.tags,
            )
        else:
            logger.error(
                "trace_context_error",
                name=self.name,
                duration=duration,
                error=str(exc_val),
            )
