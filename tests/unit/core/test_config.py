"""Tests for configuration management."""

import pytest
from pydantic import ValidationError

from psyai.core.config import Settings, get_settings


class TestSettings:
    """Tests for Settings class."""

    def test_default_settings(self):
        """Test that default settings load correctly."""
        settings = Settings()

        assert settings.app_name == "PsyAI"
        assert settings.app_env == "development"
        assert settings.app_debug is True
        assert settings.log_level == "INFO"

    def test_settings_validation_app_env(self):
        """Test app_env validation."""
        with pytest.raises(ValidationError):
            Settings(app_env="invalid")

    def test_settings_validation_log_level(self):
        """Test log_level validation."""
        # Should normalize to uppercase
        settings = Settings(log_level="debug")
        assert settings.log_level == "DEBUG"

    def test_settings_validation_vector_db_type(self):
        """Test vector_db_type validation."""
        with pytest.raises(ValidationError):
            Settings(vector_db_type="invalid")

        # Should accept valid types
        settings = Settings(vector_db_type="chroma")
        assert settings.vector_db_type == "chroma"

    def test_is_development_property(self):
        """Test is_development property."""
        settings = Settings(app_env="development")
        assert settings.is_development is True
        assert settings.is_production is False
        assert settings.is_staging is False

    def test_is_production_property(self):
        """Test is_production property."""
        settings = Settings(app_env="production")
        assert settings.is_production is True
        assert settings.is_development is False
        assert settings.is_staging is False

    def test_is_staging_property(self):
        """Test is_staging property."""
        settings = Settings(app_env="staging")
        assert settings.is_staging is True
        assert settings.is_development is False
        assert settings.is_production is False

    def test_get_database_url_async(self):
        """Test async database URL generation."""
        settings = Settings(database_url="postgresql://user:pass@localhost/db")
        async_url = settings.get_database_url_async()

        assert async_url == "postgresql+asyncpg://user:pass@localhost/db"

    def test_model_dump_safe(self):
        """Test that model_dump_safe masks sensitive data."""
        settings = Settings(
            secret_key="my-secret-key",
            openai_api_key="sk-1234567890",
            database_url="postgresql://user:pass@localhost/db",
        )

        safe_dump = settings.model_dump_safe()

        assert safe_dump["secret_key"] == "***MASKED***"
        assert safe_dump["openai_api_key"] == "***MASKED***"
        assert safe_dump["database_url"] == "***MASKED***"
        assert safe_dump["app_name"] == "PsyAI"  # Non-sensitive field


class TestGetSettings:
    """Tests for get_settings function."""

    def test_get_settings_returns_singleton(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_get_settings_cache_clear(self):
        """Test that cache can be cleared."""
        settings1 = get_settings()
        get_settings.cache_clear()
        settings2 = get_settings()

        # After cache clear, should be new instance
        assert settings1 is not settings2
