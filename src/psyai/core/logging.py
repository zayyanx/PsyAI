"""
Structured logging configuration for PsyAI.

This module provides a structured logging setup using structlog
for better log analysis and debugging.
"""

import logging
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.types import EventDict, Processor

from psyai.core.config import settings


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add application context to log entries.

    Args:
        logger: Logger instance
        method_name: Method name
        event_dict: Event dictionary

    Returns:
        Enhanced event dictionary
    """
    event_dict["app"] = settings.app_name
    event_dict["env"] = settings.app_env
    return event_dict


def censor_sensitive_data(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Censor sensitive data from logs.

    Args:
        logger: Logger instance
        method_name: Method name
        event_dict: Event dictionary

    Returns:
        Censored event dictionary
    """
    sensitive_keys = [
        "password",
        "token",
        "api_key",
        "secret",
        "authorization",
        "auth",
        "access_token",
        "refresh_token",
    ]

    def _censor_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively censor dictionary values."""
        result = {}
        for key, value in d.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                result[key] = "***CENSORED***"
            elif isinstance(value, dict):
                result[key] = _censor_dict(value)
            elif isinstance(value, list):
                result[key] = [_censor_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value
        return result

    # Censor the event dict
    for key, value in list(event_dict.items()):
        if isinstance(value, dict):
            event_dict[key] = _censor_dict(value)

    return event_dict


def setup_logging(log_level: Optional[str] = None, json_logs: bool = False) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs in JSON format (recommended for production)

    Example:
        >>> setup_logging(log_level="INFO", json_logs=True)
        >>> logger = get_logger(__name__)
        >>> logger.info("application_started", version="1.0.0")
    """
    log_level = log_level or settings.log_level

    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Define processors
    shared_processors: list[Processor] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
        censor_sensitive_data,
    ]

    if json_logs:
        # JSON output for production
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Console output for development
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    # Set log level for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Structured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("user_login", user_id=123, ip="192.168.1.1")
        >>> logger.error("database_error", error="Connection timeout", table="users")
    """
    return structlog.get_logger(name)


class LoggerAdapter:
    """
    Adapter to add persistent context to logger.

    Example:
        >>> adapter = LoggerAdapter(get_logger(__name__), user_id=123)
        >>> adapter.info("action_performed", action="login")
        # Logs: {"event": "action_performed", "action": "login", "user_id": 123}
    """

    def __init__(self, logger: structlog.stdlib.BoundLogger, **context: Any):
        """
        Initialize logger adapter with context.

        Args:
            logger: Base logger instance
            **context: Context to add to all log entries
        """
        self.logger = logger.bind(**context)

    def debug(self, event: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.logger.debug(event, **kwargs)

    def info(self, event: str, **kwargs: Any) -> None:
        """Log info message."""
        self.logger.info(event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.logger.warning(event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        """Log error message."""
        self.logger.error(event, **kwargs)

    def critical(self, event: str, **kwargs: Any) -> None:
        """Log critical message."""
        self.logger.critical(event, **kwargs)

    def exception(self, event: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self.logger.exception(event, **kwargs)


# Initialize logging on module import
setup_logging(json_logs=settings.is_production)

# Export default logger
logger = get_logger("psyai")
