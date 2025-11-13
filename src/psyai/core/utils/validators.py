"""
Common validation utilities.

Provides reusable validation functions for data validation across the application.
"""

import re
from typing import Any, Dict, List, Optional
from uuid import UUID

from psyai.core.exceptions import ValidationError


def validate_email(email: str) -> str:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        Validated email address (lowercased)

    Raises:
        ValidationError: If email is invalid

    Example:
        >>> validate_email("user@example.com")
        'user@example.com'
        >>> validate_email("invalid")
        ValidationError: Invalid email format
    """
    email = email.strip().lower()

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        raise ValidationError(
            "Invalid email format",
            details={"email": email},
        )

    return email


def validate_uuid(value: str, field_name: str = "id") -> UUID:
    """
    Validate UUID string format.

    Args:
        value: UUID string to validate
        field_name: Name of the field (for error messages)

    Returns:
        UUID object

    Raises:
        ValidationError: If UUID is invalid

    Example:
        >>> validate_uuid("123e4567-e89b-12d3-a456-426614174000")
        UUID('123e4567-e89b-12d3-a456-426614174000')
    """
    try:
        return UUID(value)
    except (ValueError, AttributeError) as e:
        raise ValidationError(
            f"Invalid UUID format for {field_name}",
            details={"value": value, "error": str(e)},
        )


def validate_string_length(
    value: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    field_name: str = "value",
) -> str:
    """
    Validate string length.

    Args:
        value: String to validate
        min_length: Minimum length (inclusive)
        max_length: Maximum length (inclusive)
        field_name: Name of the field (for error messages)

    Returns:
        Validated string

    Raises:
        ValidationError: If length is invalid

    Example:
        >>> validate_string_length("hello", min_length=1, max_length=10)
        'hello'
    """
    length = len(value)

    if min_length is not None and length < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters",
            details={"value": value, "length": length, "min_length": min_length},
        )

    if max_length is not None and length > max_length:
        raise ValidationError(
            f"{field_name} must not exceed {max_length} characters",
            details={"value": value, "length": length, "max_length": max_length},
        )

    return value


def validate_number_range(
    value: float,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    field_name: str = "value",
) -> float:
    """
    Validate number is within range.

    Args:
        value: Number to validate
        min_value: Minimum value (inclusive)
        max_value: Maximum value (inclusive)
        field_name: Name of the field (for error messages)

    Returns:
        Validated number

    Raises:
        ValidationError: If value is out of range

    Example:
        >>> validate_number_range(5.0, min_value=0.0, max_value=10.0)
        5.0
    """
    if min_value is not None and value < min_value:
        raise ValidationError(
            f"{field_name} must be at least {min_value}",
            details={"value": value, "min_value": min_value},
        )

    if max_value is not None and value > max_value:
        raise ValidationError(
            f"{field_name} must not exceed {max_value}",
            details={"value": value, "max_value": max_value},
        )

    return value


def validate_non_empty(value: Any, field_name: str = "value") -> Any:
    """
    Validate that value is not empty.

    Args:
        value: Value to validate
        field_name: Name of the field (for error messages)

    Returns:
        Validated value

    Raises:
        ValidationError: If value is empty

    Example:
        >>> validate_non_empty("hello")
        'hello'
        >>> validate_non_empty("")
        ValidationError: value cannot be empty
    """
    if value is None:
        raise ValidationError(
            f"{field_name} cannot be None",
            details={"field": field_name},
        )

    if isinstance(value, (str, list, dict)) and len(value) == 0:
        raise ValidationError(
            f"{field_name} cannot be empty",
            details={"field": field_name, "type": type(value).__name__},
        )

    return value


def validate_choice(
    value: str,
    choices: List[str],
    field_name: str = "value",
    case_sensitive: bool = True,
) -> str:
    """
    Validate value is one of allowed choices.

    Args:
        value: Value to validate
        choices: List of allowed choices
        field_name: Name of the field (for error messages)
        case_sensitive: Whether comparison is case-sensitive

    Returns:
        Validated value

    Raises:
        ValidationError: If value is not in choices

    Example:
        >>> validate_choice("red", ["red", "green", "blue"])
        'red'
    """
    comparison_value = value if case_sensitive else value.lower()
    comparison_choices = choices if case_sensitive else [c.lower() for c in choices]

    if comparison_value not in comparison_choices:
        raise ValidationError(
            f"{field_name} must be one of: {', '.join(choices)}",
            details={"value": value, "choices": choices},
        )

    return value


def validate_dict_keys(
    data: Dict[str, Any],
    required_keys: Optional[List[str]] = None,
    optional_keys: Optional[List[str]] = None,
    allow_extra: bool = False,
) -> Dict[str, Any]:
    """
    Validate dictionary has required keys and no unexpected keys.

    Args:
        data: Dictionary to validate
        required_keys: List of required keys
        optional_keys: List of optional keys
        allow_extra: Whether to allow extra keys

    Returns:
        Validated dictionary

    Raises:
        ValidationError: If validation fails

    Example:
        >>> validate_dict_keys(
        ...     {"name": "John", "age": 30},
        ...     required_keys=["name"],
        ...     optional_keys=["age"]
        ... )
        {'name': 'John', 'age': 30}
    """
    required_keys = required_keys or []
    optional_keys = optional_keys or []
    allowed_keys = set(required_keys + optional_keys)

    # Check required keys
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        raise ValidationError(
            f"Missing required keys: {', '.join(missing_keys)}",
            details={"missing_keys": missing_keys},
        )

    # Check for unexpected keys
    if not allow_extra:
        extra_keys = [key for key in data.keys() if key not in allowed_keys]
        if extra_keys:
            raise ValidationError(
                f"Unexpected keys: {', '.join(extra_keys)}",
                details={"extra_keys": extra_keys, "allowed_keys": list(allowed_keys)},
            )

    return data


def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> str:
    """
    Validate URL format.

    Args:
        url: URL to validate
        allowed_schemes: List of allowed schemes (e.g., ['http', 'https'])

    Returns:
        Validated URL

    Raises:
        ValidationError: If URL is invalid

    Example:
        >>> validate_url("https://example.com")
        'https://example.com'
    """
    url = url.strip()

    # Basic URL pattern
    pattern = r"^https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})?(?:/.*)?$"

    if not re.match(pattern, url):
        raise ValidationError(
            "Invalid URL format",
            details={"url": url},
        )

    if allowed_schemes:
        scheme = url.split("://")[0]
        if scheme not in allowed_schemes:
            raise ValidationError(
                f"URL scheme must be one of: {', '.join(allowed_schemes)}",
                details={"url": url, "scheme": scheme, "allowed_schemes": allowed_schemes},
            )

    return url


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string by removing dangerous characters.

    Args:
        value: String to sanitize
        max_length: Maximum length to truncate to

    Returns:
        Sanitized string

    Example:
        >>> sanitize_string("<script>alert('xss')</script>")
        'scriptalert(xss)/script'
    """
    # Remove potentially dangerous characters for basic XSS prevention
    dangerous_chars = ["<", ">", '"', "'", "&", ";"]
    sanitized = value

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")

    sanitized = sanitized.strip()

    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized
