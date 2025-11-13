"""
Exception classes for PsyAI.

This module defines the exception hierarchy used throughout the application.
All exceptions inherit from PsyAIException for consistent error handling.
"""

from typing import Any, Dict, Optional


class PsyAIException(Exception):
    """
    Base exception for all PsyAI exceptions.

    Attributes:
        message: Human-readable error message
        code: Error code for programmatic handling
        details: Additional error details
    """

    def __init__(
        self,
        message: str,
        code: str = "PSYAI_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize exception.

        Args:
            message: Error message
            code: Error code
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary.

        Returns:
            Dictionary representation of the exception
        """
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }

    def __str__(self) -> str:
        """String representation."""
        if self.details:
            return f"{self.code}: {self.message} (details: {self.details})"
        return f"{self.code}: {self.message}"


# Configuration Exceptions
class ConfigurationError(PsyAIException):
    """Exception raised for configuration errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CONFIGURATION_ERROR", details=details)


class ValidationError(PsyAIException):
    """Exception raised for validation errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


# Database Exceptions
class DatabaseError(PsyAIException):
    """Base exception for database errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="DATABASE_ERROR", details=details)


class DatabaseConnectionError(DatabaseError):
    """Exception raised when database connection fails."""

    def __init__(self, message: str = "Failed to connect to database", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details=details)
        self.code = "DATABASE_CONNECTION_ERROR"


class RecordNotFoundError(DatabaseError):
    """Exception raised when a database record is not found."""

    def __init__(self, resource: str, identifier: Any, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} not found: {identifier}"
        super().__init__(message, details=details)
        self.code = "RECORD_NOT_FOUND"
        self.resource = resource
        self.identifier = identifier


class DuplicateRecordError(DatabaseError):
    """Exception raised when attempting to create a duplicate record."""

    def __init__(self, resource: str, field: str, value: Any, details: Optional[Dict[str, Any]] = None):
        message = f"Duplicate {resource}: {field}={value} already exists"
        super().__init__(message, details=details)
        self.code = "DUPLICATE_RECORD"


# API Exceptions
class APIError(PsyAIException):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code="API_ERROR", details=details)
        self.status_code = status_code


class AuthenticationError(APIError):
    """Exception raised for authentication failures."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)
        self.code = "AUTHENTICATION_ERROR"


class AuthorizationError(APIError):
    """Exception raised for authorization failures."""

    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)
        self.code = "AUTHORIZATION_ERROR"


class RateLimitExceededError(APIError):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=429, details=details)
        self.code = "RATE_LIMIT_EXCEEDED"
        self.retry_after = retry_after


# LangChain/LLM Exceptions
class LLMError(PsyAIException):
    """Base exception for LLM-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="LLM_ERROR", details=details)


class LLMTimeoutError(LLMError):
    """Exception raised when LLM request times out."""

    def __init__(self, message: str = "LLM request timed out", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details=details)
        self.code = "LLM_TIMEOUT"


class LLMRateLimitError(LLMError):
    """Exception raised when LLM rate limit is hit."""

    def __init__(self, message: str = "LLM rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details=details)
        self.code = "LLM_RATE_LIMIT"


class LLMInvalidResponseError(LLMError):
    """Exception raised when LLM returns invalid response."""

    def __init__(self, message: str = "Invalid LLM response", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details=details)
        self.code = "LLM_INVALID_RESPONSE"


# Centaur Model Exceptions
class CentaurError(PsyAIException):
    """Base exception for Centaur model errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CENTAUR_ERROR", details=details)


class CentaurAPIError(CentaurError):
    """Exception raised for Centaur API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details=details)
        self.code = "CENTAUR_API_ERROR"
        self.status_code = status_code


class CentaurUnavailableError(CentaurError):
    """Exception raised when Centaur service is unavailable."""

    def __init__(self, message: str = "Centaur service unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details=details)
        self.code = "CENTAUR_UNAVAILABLE"


# Evaluation Exceptions
class EvaluationError(PsyAIException):
    """Base exception for evaluation errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="EVALUATION_ERROR", details=details)


class EvaluationFailedError(EvaluationError):
    """Exception raised when evaluation fails quality thresholds."""

    def __init__(
        self,
        message: str,
        score: float,
        threshold: float,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details=details)
        self.code = "EVALUATION_FAILED"
        self.score = score
        self.threshold = threshold


# Chat Exceptions
class ChatError(PsyAIException):
    """Base exception for chat-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CHAT_ERROR", details=details)


class SessionNotFoundError(ChatError):
    """Exception raised when chat session is not found."""

    def __init__(self, session_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"Chat session not found: {session_id}"
        super().__init__(message, details=details)
        self.code = "SESSION_NOT_FOUND"
        self.session_id = session_id


class ExpertUnavailableError(ChatError):
    """Exception raised when no expert is available."""

    def __init__(self, message: str = "No expert available", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details=details)
        self.code = "EXPERT_UNAVAILABLE"


# Storage Exceptions
class StorageError(PsyAIException):
    """Base exception for storage errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="STORAGE_ERROR", details=details)


class VectorStoreError(StorageError):
    """Exception raised for vector store errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details=details)
        self.code = "VECTOR_STORE_ERROR"


class CacheError(StorageError):
    """Exception raised for cache errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details=details)
        self.code = "CACHE_ERROR"


# External Service Exceptions
class ExternalServiceError(PsyAIException):
    """Base exception for external service errors."""

    def __init__(
        self,
        service: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code="EXTERNAL_SERVICE_ERROR", details=details)
        self.service = service


class ServiceTimeoutError(ExternalServiceError):
    """Exception raised when external service times out."""

    def __init__(self, service: str, timeout: int, details: Optional[Dict[str, Any]] = None):
        message = f"{service} timed out after {timeout}s"
        super().__init__(service, message, details=details)
        self.code = "SERVICE_TIMEOUT"
        self.timeout = timeout


class ServiceUnavailableError(ExternalServiceError):
    """Exception raised when external service is unavailable."""

    def __init__(self, service: str, details: Optional[Dict[str, Any]] = None):
        message = f"{service} is unavailable"
        super().__init__(service, message, details=details)
        self.code = "SERVICE_UNAVAILABLE"


# Feature-specific Exceptions
class HITLError(PsyAIException):
    """Base exception for Human-in-the-Loop errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="HITL_ERROR", details=details)


class ReviewQueueEmptyError(HITLError):
    """Exception raised when review queue is empty."""

    def __init__(self, message: str = "Review queue is empty", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details=details)
        self.code = "REVIEW_QUEUE_EMPTY"


class ReviewNotFoundError(HITLError):
    """Exception raised when review item is not found."""

    def __init__(self, review_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"Review item not found: {review_id}"
        super().__init__(message, details=details)
        self.code = "REVIEW_NOT_FOUND"
        self.review_id = review_id


# Utility functions for exception handling
def handle_exception(exc: Exception) -> Dict[str, Any]:
    """
    Convert any exception to a standard error dictionary.

    Args:
        exc: Exception to handle

    Returns:
        Error dictionary

    Example:
        >>> try:
        ...     raise ValidationError("Invalid input")
        ... except Exception as e:
        ...     error_dict = handle_exception(e)
    """
    if isinstance(exc, PsyAIException):
        return exc.to_dict()

    # Handle standard exceptions
    return {
        "error": "INTERNAL_ERROR",
        "message": str(exc),
        "details": {"type": exc.__class__.__name__},
    }
