"""Tests for validation utilities."""

import pytest
from uuid import UUID

from psyai.core.exceptions import ValidationError
from psyai.core.utils.validators import (
    sanitize_string,
    validate_choice,
    validate_dict_keys,
    validate_email,
    validate_non_empty,
    validate_number_range,
    validate_string_length,
    validate_url,
    validate_uuid,
)


class TestValidateEmail:
    """Tests for email validation."""

    def test_valid_email(self):
        """Test valid email addresses."""
        assert validate_email("test@example.com") == "test@example.com"
        assert validate_email("user.name@example.co.uk") == "user.name@example.co.uk"
        assert validate_email("  TEST@EXAMPLE.COM  ") == "test@example.com"  # Should lowercase

    def test_invalid_email(self):
        """Test invalid email addresses."""
        with pytest.raises(ValidationError):
            validate_email("invalid")

        with pytest.raises(ValidationError):
            validate_email("@example.com")

        with pytest.raises(ValidationError):
            validate_email("user@")


class TestValidateUUID:
    """Tests for UUID validation."""

    def test_valid_uuid(self):
        """Test valid UUIDs."""
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"
        result = validate_uuid(uuid_str)

        assert isinstance(result, UUID)
        assert str(result) == uuid_str

    def test_invalid_uuid(self):
        """Test invalid UUIDs."""
        with pytest.raises(ValidationError):
            validate_uuid("not-a-uuid")

        with pytest.raises(ValidationError):
            validate_uuid("12345")


class TestValidateStringLength:
    """Tests for string length validation."""

    def test_valid_length(self):
        """Test valid string lengths."""
        assert validate_string_length("hello", min_length=1, max_length=10) == "hello"
        assert validate_string_length("test", min_length=4, max_length=4) == "test"

    def test_too_short(self):
        """Test string too short."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_length("hi", min_length=5)

        assert "at least 5 characters" in str(exc_info.value)

    def test_too_long(self):
        """Test string too long."""
        with pytest.raises(ValidationError) as exc_info:
            validate_string_length("hello world", max_length=5)

        assert "not exceed 5 characters" in str(exc_info.value)


class TestValidateNumberRange:
    """Tests for number range validation."""

    def test_valid_range(self):
        """Test valid number ranges."""
        assert validate_number_range(5.0, min_value=0.0, max_value=10.0) == 5.0
        assert validate_number_range(0.0, min_value=0.0, max_value=10.0) == 0.0
        assert validate_number_range(10.0, min_value=0.0, max_value=10.0) == 10.0

    def test_below_minimum(self):
        """Test number below minimum."""
        with pytest.raises(ValidationError) as exc_info:
            validate_number_range(-1.0, min_value=0.0)

        assert "at least 0.0" in str(exc_info.value)

    def test_above_maximum(self):
        """Test number above maximum."""
        with pytest.raises(ValidationError) as exc_info:
            validate_number_range(11.0, max_value=10.0)

        assert "not exceed 10.0" in str(exc_info.value)


class TestValidateNonEmpty:
    """Tests for non-empty validation."""

    def test_valid_non_empty(self):
        """Test valid non-empty values."""
        assert validate_non_empty("hello") == "hello"
        assert validate_non_empty([1, 2, 3]) == [1, 2, 3]
        assert validate_non_empty({"key": "value"}) == {"key": "value"}

    def test_none_value(self):
        """Test None value."""
        with pytest.raises(ValidationError) as exc_info:
            validate_non_empty(None)

        assert "cannot be None" in str(exc_info.value)

    def test_empty_string(self):
        """Test empty string."""
        with pytest.raises(ValidationError) as exc_info:
            validate_non_empty("")

        assert "cannot be empty" in str(exc_info.value)

    def test_empty_list(self):
        """Test empty list."""
        with pytest.raises(ValidationError):
            validate_non_empty([])

    def test_empty_dict(self):
        """Test empty dict."""
        with pytest.raises(ValidationError):
            validate_non_empty({})


class TestValidateChoice:
    """Tests for choice validation."""

    def test_valid_choice(self):
        """Test valid choices."""
        assert validate_choice("red", ["red", "green", "blue"]) == "red"

    def test_invalid_choice(self):
        """Test invalid choices."""
        with pytest.raises(ValidationError) as exc_info:
            validate_choice("yellow", ["red", "green", "blue"])

        assert "must be one of" in str(exc_info.value)

    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        assert validate_choice("RED", ["red", "green", "blue"], case_sensitive=False) == "RED"

    def test_case_sensitive(self):
        """Test case-sensitive matching."""
        with pytest.raises(ValidationError):
            validate_choice("RED", ["red", "green", "blue"], case_sensitive=True)


class TestValidateDictKeys:
    """Tests for dictionary key validation."""

    def test_valid_dict(self):
        """Test valid dictionary."""
        data = {"name": "John", "age": 30}
        result = validate_dict_keys(
            data,
            required_keys=["name"],
            optional_keys=["age", "email"],
        )
        assert result == data

    def test_missing_required_keys(self):
        """Test missing required keys."""
        data = {"age": 30}

        with pytest.raises(ValidationError) as exc_info:
            validate_dict_keys(data, required_keys=["name", "email"])

        assert "Missing required keys" in str(exc_info.value)

    def test_unexpected_keys(self):
        """Test unexpected keys."""
        data = {"name": "John", "extra": "value"}

        with pytest.raises(ValidationError) as exc_info:
            validate_dict_keys(data, required_keys=["name"])

        assert "Unexpected keys" in str(exc_info.value)

    def test_allow_extra_keys(self):
        """Test allowing extra keys."""
        data = {"name": "John", "extra": "value"}
        result = validate_dict_keys(
            data,
            required_keys=["name"],
            allow_extra=True,
        )
        assert result == data


class TestValidateURL:
    """Tests for URL validation."""

    def test_valid_url(self):
        """Test valid URLs."""
        assert validate_url("https://example.com") == "https://example.com"
        assert validate_url("http://example.com/path") == "http://example.com/path"

    def test_invalid_url(self):
        """Test invalid URLs."""
        with pytest.raises(ValidationError):
            validate_url("not-a-url")

        with pytest.raises(ValidationError):
            validate_url("ftp://example.com")  # Wrong scheme

    def test_allowed_schemes(self):
        """Test allowed schemes validation."""
        validate_url("https://example.com", allowed_schemes=["https"])

        with pytest.raises(ValidationError):
            validate_url("http://example.com", allowed_schemes=["https"])


class TestSanitizeString:
    """Tests for string sanitization."""

    def test_sanitize_dangerous_chars(self):
        """Test removal of dangerous characters."""
        result = sanitize_string("<script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result
        assert "script" in result

    def test_sanitize_with_max_length(self):
        """Test sanitization with max length."""
        result = sanitize_string("hello world", max_length=5)
        assert result == "hello"

    def test_sanitize_strips_whitespace(self):
        """Test that sanitization strips whitespace."""
        result = sanitize_string("  hello  ")
        assert result == "hello"
