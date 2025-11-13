"""Tests for exception classes."""

import pytest

from psyai.core.exceptions import (
    AuthenticationError,
    CentaurAPIError,
    DatabaseConnectionError,
    DuplicateRecordError,
    EvaluationFailedError,
    LLMTimeoutError,
    PsyAIException,
    RateLimitExceededError,
    RecordNotFoundError,
    ValidationError,
    handle_exception,
)


class TestPsyAIException:
    """Tests for base PsyAIException class."""

    def test_basic_exception(self):
        """Test basic exception creation."""
        exc = PsyAIException("Test error")

        assert str(exc) == "PSYAI_ERROR: Test error"
        assert exc.message == "Test error"
        assert exc.code == "PSYAI_ERROR"
        assert exc.details == {}

    def test_exception_with_code(self):
        """Test exception with custom code."""
        exc = PsyAIException("Test error", code="CUSTOM_ERROR")

        assert exc.code == "CUSTOM_ERROR"
        assert str(exc) == "CUSTOM_ERROR: Test error"

    def test_exception_with_details(self):
        """Test exception with details."""
        details = {"field": "username", "value": "test"}
        exc = PsyAIException("Test error", details=details)

        assert exc.details == details
        assert "field" in str(exc)

    def test_to_dict(self):
        """Test exception to_dict method."""
        details = {"field": "username"}
        exc = PsyAIException("Test error", code="TEST_ERROR", details=details)

        result = exc.to_dict()

        assert result["error"] == "TEST_ERROR"
        assert result["message"] == "Test error"
        assert result["details"] == details


class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_configuration_error(self):
        """Test ConfigurationError creation."""
        exc = ValidationError("Invalid config")

        assert exc.code == "VALIDATION_ERROR"
        assert exc.message == "Invalid config"


class TestDatabaseExceptions:
    """Tests for database exceptions."""

    def test_database_connection_error(self):
        """Test DatabaseConnectionError."""
        exc = DatabaseConnectionError()

        assert exc.code == "DATABASE_CONNECTION_ERROR"
        assert "connect" in exc.message.lower()

    def test_record_not_found_error(self):
        """Test RecordNotFoundError."""
        exc = RecordNotFoundError("User", 123)

        assert exc.code == "RECORD_NOT_FOUND"
        assert exc.resource == "User"
        assert exc.identifier == 123
        assert "User" in exc.message
        assert "123" in exc.message

    def test_duplicate_record_error(self):
        """Test DuplicateRecordError."""
        exc = DuplicateRecordError("User", "email", "test@example.com")

        assert exc.code == "DUPLICATE_RECORD"
        assert "email" in exc.message
        assert "test@example.com" in exc.message


class TestAPIExceptions:
    """Tests for API exceptions."""

    def test_authentication_error(self):
        """Test AuthenticationError."""
        exc = AuthenticationError()

        assert exc.code == "AUTHENTICATION_ERROR"
        assert exc.status_code == 401

    def test_rate_limit_exceeded_error(self):
        """Test RateLimitExceededError."""
        exc = RateLimitExceededError(retry_after=60)

        assert exc.code == "RATE_LIMIT_EXCEEDED"
        assert exc.status_code == 429
        assert exc.retry_after == 60


class TestLLMExceptions:
    """Tests for LLM exceptions."""

    def test_llm_timeout_error(self):
        """Test LLMTimeoutError."""
        exc = LLMTimeoutError()

        assert exc.code == "LLM_TIMEOUT"
        assert ("timeout" in exc.message.lower() or "timed out" in exc.message.lower())


class TestCentaurExceptions:
    """Tests for Centaur exceptions."""

    def test_centaur_api_error(self):
        """Test CentaurAPIError."""
        exc = CentaurAPIError("API error", status_code=500)

        assert exc.code == "CENTAUR_API_ERROR"
        assert exc.status_code == 500


class TestEvaluationExceptions:
    """Tests for evaluation exceptions."""

    def test_evaluation_failed_error(self):
        """Test EvaluationFailedError."""
        exc = EvaluationFailedError(
            "Evaluation failed",
            score=0.5,
            threshold=0.7,
        )

        assert exc.code == "EVALUATION_FAILED"
        assert exc.score == 0.5
        assert exc.threshold == 0.7


class TestHandleException:
    """Tests for handle_exception utility."""

    def test_handle_psyai_exception(self):
        """Test handling PsyAI exceptions."""
        exc = ValidationError("Invalid input", details={"field": "username"})
        result = handle_exception(exc)

        assert result["error"] == "VALIDATION_ERROR"
        assert result["message"] == "Invalid input"
        assert result["details"]["field"] == "username"

    def test_handle_standard_exception(self):
        """Test handling standard Python exceptions."""
        exc = ValueError("Invalid value")
        result = handle_exception(exc)

        assert result["error"] == "INTERNAL_ERROR"
        assert result["message"] == "Invalid value"
        assert result["details"]["type"] == "ValueError"
