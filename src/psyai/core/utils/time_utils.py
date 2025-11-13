"""
Time utilities for PsyAI.

Provides helper functions for working with dates and times.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional


def utcnow() -> datetime:
    """
    Get current UTC datetime.

    Returns:
        Current UTC datetime with timezone info

    Example:
        >>> now = utcnow()
        >>> print(now.tzinfo)
        UTC
    """
    return datetime.now(timezone.utc)


def from_timestamp(timestamp: float) -> datetime:
    """
    Convert Unix timestamp to datetime.

    Args:
        timestamp: Unix timestamp (seconds since epoch)

    Returns:
        Datetime with UTC timezone

    Example:
        >>> dt = from_timestamp(1609459200)  # 2021-01-01 00:00:00 UTC
    """
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def to_timestamp(dt: datetime) -> float:
    """
    Convert datetime to Unix timestamp.

    Args:
        dt: Datetime object

    Returns:
        Unix timestamp (seconds since epoch)

    Example:
        >>> dt = utcnow()
        >>> timestamp = to_timestamp(dt)
    """
    return dt.timestamp()


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime as string.

    Args:
        dt: Datetime object
        fmt: Format string (strftime format)

    Returns:
        Formatted datetime string

    Example:
        >>> dt = utcnow()
        >>> format_datetime(dt)
        '2025-11-13 10:30:45'
    """
    return dt.strftime(fmt)


def parse_datetime(dt_string: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse datetime string.

    Args:
        dt_string: Datetime string
        fmt: Format string (strptime format)

    Returns:
        Datetime object with UTC timezone

    Example:
        >>> dt = parse_datetime("2025-11-13 10:30:45")
    """
    dt = datetime.strptime(dt_string, fmt)
    # Add UTC timezone if not present
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def time_ago(dt: datetime, now: Optional[datetime] = None) -> str:
    """
    Get human-readable "time ago" string.

    Args:
        dt: Past datetime
        now: Reference datetime (defaults to current time)

    Returns:
        Human-readable string (e.g., "2 hours ago")

    Example:
        >>> past = utcnow() - timedelta(hours=2)
        >>> time_ago(past)
        '2 hours ago'
    """
    if now is None:
        now = utcnow()

    # Ensure both datetimes have timezone info
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"


def is_expired(dt: datetime, ttl_seconds: int, now: Optional[datetime] = None) -> bool:
    """
    Check if datetime has expired based on TTL.

    Args:
        dt: Datetime to check
        ttl_seconds: Time to live in seconds
        now: Reference datetime (defaults to current time)

    Returns:
        True if expired, False otherwise

    Example:
        >>> created_at = utcnow() - timedelta(hours=2)
        >>> is_expired(created_at, ttl_seconds=3600)  # 1 hour TTL
        True
    """
    if now is None:
        now = utcnow()

    # Ensure both datetimes have timezone info
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    expiry_time = dt + timedelta(seconds=ttl_seconds)
    return now > expiry_time


def add_time(dt: datetime, **kwargs: int) -> datetime:
    """
    Add time to datetime.

    Args:
        dt: Datetime object
        **kwargs: Keyword arguments for timedelta (days, hours, minutes, seconds, etc.)

    Returns:
        New datetime with added time

    Example:
        >>> dt = utcnow()
        >>> future = add_time(dt, hours=2, minutes=30)
    """
    return dt + timedelta(**kwargs)


def subtract_time(dt: datetime, **kwargs: int) -> datetime:
    """
    Subtract time from datetime.

    Args:
        dt: Datetime object
        **kwargs: Keyword arguments for timedelta (days, hours, minutes, seconds, etc.)

    Returns:
        New datetime with subtracted time

    Example:
        >>> dt = utcnow()
        >>> past = subtract_time(dt, days=7)
    """
    return dt - timedelta(**kwargs)


def start_of_day(dt: datetime) -> datetime:
    """
    Get start of day (midnight) for given datetime.

    Args:
        dt: Datetime object

    Returns:
        Datetime at midnight

    Example:
        >>> dt = utcnow()
        >>> start = start_of_day(dt)
        >>> print(start.hour, start.minute, start.second)
        0 0 0
    """
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(dt: datetime) -> datetime:
    """
    Get end of day (23:59:59) for given datetime.

    Args:
        dt: Datetime object

    Returns:
        Datetime at end of day

    Example:
        >>> dt = utcnow()
        >>> end = end_of_day(dt)
        >>> print(end.hour, end.minute, end.second)
        23 59 59
    """
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def days_between(start: datetime, end: datetime) -> int:
    """
    Calculate number of days between two datetimes.

    Args:
        start: Start datetime
        end: End datetime

    Returns:
        Number of days (can be negative)

    Example:
        >>> start = utcnow()
        >>> end = add_time(start, days=7)
        >>> days_between(start, end)
        7
    """
    # Ensure both datetimes have timezone info
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    diff = end - start
    return diff.days


def seconds_between(start: datetime, end: datetime) -> float:
    """
    Calculate number of seconds between two datetimes.

    Args:
        start: Start datetime
        end: End datetime

    Returns:
        Number of seconds (can be negative)

    Example:
        >>> start = utcnow()
        >>> end = add_time(start, hours=2)
        >>> seconds_between(start, end)
        7200.0
    """
    # Ensure both datetimes have timezone info
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    diff = end - start
    return diff.total_seconds()
