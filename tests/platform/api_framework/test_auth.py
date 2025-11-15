"""Tests for authentication."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from jose import jwt

from psyai.core.exceptions import AuthenticationError
from psyai.platform.api_framework.auth import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing functions."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password("wrongpassword", hashed) is False

    def test_different_hashes(self):
        """Test that same password generates different hashes."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Different hashes due to salt
        assert hash1 != hash2

        # But both verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWT:
    """Test JWT token functions."""

    @patch("psyai.platform.api_framework.auth.jwt.settings")
    def test_create_access_token(self, mock_settings):
        """Test creating access token."""
        mock_settings.secret_key = "test-secret-key"
        mock_settings.algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 30

        data = {"sub": 123, "email": "test@example.com"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    @patch("psyai.platform.api_framework.auth.jwt.settings")
    def test_create_access_token_with_expiry(self, mock_settings):
        """Test creating token with custom expiry."""
        mock_settings.secret_key = "test-secret-key"
        mock_settings.algorithm = "HS256"

        data = {"sub": 123}
        expires_delta = timedelta(hours=1)
        token = create_access_token(data, expires_delta)

        assert isinstance(token, str)

    @patch("psyai.platform.api_framework.auth.jwt.settings")
    def test_decode_access_token(self, mock_settings):
        """Test decoding access token."""
        mock_settings.secret_key = "test-secret-key"
        mock_settings.algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 30

        data = {"sub": 123, "email": "test@example.com"}
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert decoded["sub"] == 123
        assert decoded["email"] == "test@example.com"
        assert "exp" in decoded

    @patch("psyai.platform.api_framework.auth.jwt.settings")
    def test_decode_invalid_token(self, mock_settings):
        """Test decoding invalid token."""
        mock_settings.secret_key = "test-secret-key"
        mock_settings.algorithm = "HS256"

        with pytest.raises(AuthenticationError):
            decode_access_token("invalid.token.here")

    @patch("psyai.platform.api_framework.auth.jwt.settings")
    def test_decode_expired_token(self, mock_settings):
        """Test decoding expired token."""
        mock_settings.secret_key = "test-secret-key"
        mock_settings.algorithm = "HS256"

        # Create already expired token
        data = {"sub": 123}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta)

        with pytest.raises(AuthenticationError):
            decode_access_token(token)

    @patch("psyai.platform.api_framework.auth.jwt.settings")
    def test_decode_wrong_secret(self, mock_settings):
        """Test decoding with wrong secret key."""
        mock_settings.secret_key = "test-secret-key"
        mock_settings.algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 30

        data = {"sub": 123}
        token = create_access_token(data)

        # Try to decode with different secret
        mock_settings.secret_key = "different-secret"

        with pytest.raises(AuthenticationError):
            decode_access_token(token)
