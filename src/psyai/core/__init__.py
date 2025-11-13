"""
Core infrastructure for PsyAI.

This module provides foundational components including:
- Configuration management
- Structured logging
- Exception classes
- Utility functions
"""

from psyai.core.config import Settings, get_settings, settings
from psyai.core.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    CacheError,
    CentaurAPIError,
    CentaurError,
    CentaurUnavailableError,
    ChatError,
    ConfigurationError,
    DatabaseConnectionError,
    DatabaseError,
    DuplicateRecordError,
    EvaluationError,
    EvaluationFailedError,
    ExpertUnavailableError,
    ExternalServiceError,
    HITLError,
    LLMError,
    LLMInvalidResponseError,
    LLMRateLimitError,
    LLMTimeoutError,
    PsyAIException,
    RateLimitExceededError,
    RecordNotFoundError,
    ReviewNotFoundError,
    ReviewQueueEmptyError,
    ServiceTimeoutError,
    ServiceUnavailableError,
    SessionNotFoundError,
    StorageError,
    ValidationError,
    VectorStoreError,
    handle_exception,
)
from psyai.core.logging import LoggerAdapter, get_logger, logger, setup_logging

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Configuration
    "Settings",
    "get_settings",
    "settings",
    # Logging
    "LoggerAdapter",
    "get_logger",
    "logger",
    "setup_logging",
    # Exceptions
    "APIError",
    "AuthenticationError",
    "AuthorizationError",
    "CacheError",
    "CentaurAPIError",
    "CentaurError",
    "CentaurUnavailableError",
    "ChatError",
    "ConfigurationError",
    "DatabaseConnectionError",
    "DatabaseError",
    "DuplicateRecordError",
    "EvaluationError",
    "EvaluationFailedError",
    "ExpertUnavailableError",
    "ExternalServiceError",
    "HITLError",
    "LLMError",
    "LLMInvalidResponseError",
    "LLMRateLimitError",
    "LLMTimeoutError",
    "PsyAIException",
    "RateLimitExceededError",
    "RecordNotFoundError",
    "ReviewNotFoundError",
    "ReviewQueueEmptyError",
    "ServiceTimeoutError",
    "ServiceUnavailableError",
    "SessionNotFoundError",
    "StorageError",
    "ValidationError",
    "VectorStoreError",
    "handle_exception",
]
