"""Tests for time utilities."""

from datetime import datetime, timedelta, timezone

import pytest

from psyai.core.utils.time_utils import (
    add_time,
    days_between,
    end_of_day,
    format_datetime,
    from_timestamp,
    is_expired,
    parse_datetime,
    seconds_between,
    start_of_day,
    subtract_time,
    time_ago,
    to_timestamp,
    utcnow,
)


class TestUTCNow:
    """Tests for utcnow function."""

    def test_utcnow_returns_datetime(self):
        """Test that utcnow returns datetime with UTC timezone."""
        now = utcnow()

        assert isinstance(now, datetime)
        assert now.tzinfo == timezone.utc


class TestTimestampConversion:
    """Tests for timestamp conversion functions."""

    def test_from_timestamp(self):
        """Test converting timestamp to datetime."""
        timestamp = 1609459200.0  # 2021-01-01 00:00:00 UTC
        dt = from_timestamp(timestamp)

        assert dt.year == 2021
        assert dt.month == 1
        assert dt.day == 1
        assert dt.tzinfo == timezone.utc

    def test_to_timestamp(self):
        """Test converting datetime to timestamp."""
        dt = datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        timestamp = to_timestamp(dt)

        assert timestamp == 1609459200.0


class TestDatetimeFormatting:
    """Tests for datetime formatting functions."""

    def test_format_datetime(self):
        """Test formatting datetime as string."""
        dt = datetime(2025, 11, 13, 10, 30, 45, tzinfo=timezone.utc)
        formatted = format_datetime(dt)

        assert formatted == "2025-11-13 10:30:45"

    def test_format_datetime_custom_format(self):
        """Test formatting with custom format."""
        dt = datetime(2025, 11, 13, 10, 30, 45, tzinfo=timezone.utc)
        formatted = format_datetime(dt, fmt="%Y/%m/%d")

        assert formatted == "2025/11/13"

    def test_parse_datetime(self):
        """Test parsing datetime string."""
        dt = parse_datetime("2025-11-13 10:30:45")

        assert dt.year == 2025
        assert dt.month == 11
        assert dt.day == 13
        assert dt.hour == 10
        assert dt.tzinfo == timezone.utc


class TestTimeAgo:
    """Tests for time_ago function."""

    def test_time_ago_seconds(self):
        """Test time ago for seconds."""
        now = utcnow()
        past = now - timedelta(seconds=30)

        assert time_ago(past, now) == "just now"

    def test_time_ago_minutes(self):
        """Test time ago for minutes."""
        now = utcnow()
        past = now - timedelta(minutes=5)

        assert time_ago(past, now) == "5 minutes ago"

    def test_time_ago_hours(self):
        """Test time ago for hours."""
        now = utcnow()
        past = now - timedelta(hours=2)

        assert time_ago(past, now) == "2 hours ago"

    def test_time_ago_days(self):
        """Test time ago for days."""
        now = utcnow()
        past = now - timedelta(days=3)

        assert time_ago(past, now) == "3 days ago"


class TestIsExpired:
    """Tests for is_expired function."""

    def test_not_expired(self):
        """Test when not expired."""
        now = utcnow()
        created_at = now - timedelta(seconds=30)

        assert is_expired(created_at, ttl_seconds=60, now=now) is False

    def test_expired(self):
        """Test when expired."""
        now = utcnow()
        created_at = now - timedelta(seconds=120)

        assert is_expired(created_at, ttl_seconds=60, now=now) is True


class TestTimeOperations:
    """Tests for time addition and subtraction."""

    def test_add_time(self):
        """Test adding time to datetime."""
        dt = utcnow()
        future = add_time(dt, hours=2, minutes=30)

        diff = future - dt
        assert diff.total_seconds() == 9000  # 2.5 hours in seconds

    def test_subtract_time(self):
        """Test subtracting time from datetime."""
        dt = utcnow()
        past = subtract_time(dt, days=7)

        diff = dt - past
        assert diff.days == 7


class TestDayBoundaries:
    """Tests for day boundary functions."""

    def test_start_of_day(self):
        """Test getting start of day."""
        dt = datetime(2025, 11, 13, 15, 30, 45, tzinfo=timezone.utc)
        start = start_of_day(dt)

        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0
        assert start.microsecond == 0

    def test_end_of_day(self):
        """Test getting end of day."""
        dt = datetime(2025, 11, 13, 15, 30, 45, tzinfo=timezone.utc)
        end = end_of_day(dt)

        assert end.hour == 23
        assert end.minute == 59
        assert end.second == 59


class TestTimeDifference:
    """Tests for time difference functions."""

    def test_days_between(self):
        """Test calculating days between dates."""
        start = datetime(2025, 11, 1, tzinfo=timezone.utc)
        end = datetime(2025, 11, 8, tzinfo=timezone.utc)

        assert days_between(start, end) == 7

    def test_seconds_between(self):
        """Test calculating seconds between dates."""
        start = utcnow()
        end = start + timedelta(hours=2)

        assert seconds_between(start, end) == 7200.0
