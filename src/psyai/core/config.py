"""
Configuration management for PsyAI.

This module provides centralized configuration using Pydantic Settings
for type-safe environment variable management.
"""

from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables.
    Example: APP_ENV=production python app.py
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    app_name: str = Field(default="PsyAI", description="Application name")
    app_env: str = Field(default="development", description="Environment: development, staging, production")
    app_debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_reload: bool = Field(default=True, description="Auto-reload for development")
    api_workers: int = Field(default=1, description="Number of workers")

    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", description="Secret key for JWT")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration")

    # Database Configuration
    database_url: str = Field(
        default="postgresql://psyai_user:psyai_password@localhost:5432/psyai_db",
        description="Database connection URL",
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_max_connections: int = Field(default=10, description="Max Redis connections")

    # LangChain Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="OpenAI model")
    openai_temperature: float = Field(default=0.7, description="Model temperature")
    openai_max_tokens: int = Field(default=2000, description="Max tokens")

    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    cohere_api_key: Optional[str] = Field(default=None, description="Cohere API key")
    huggingface_api_key: Optional[str] = Field(default=None, description="HuggingFace API key")

    # LangSmith Configuration
    langsmith_api_key: Optional[str] = Field(default=None, description="LangSmith API key")
    langsmith_project: str = Field(default="psyai-project", description="LangSmith project name")
    langsmith_endpoint: str = Field(
        default="https://api.smith.langchain.com",
        description="LangSmith API endpoint",
    )
    langsmith_tracing: bool = Field(default=True, description="Enable LangSmith tracing")

    # Centaur Model Configuration
    centaur_api_url: Optional[str] = Field(default=None, description="Centaur API URL")
    centaur_api_key: Optional[str] = Field(default=None, description="Centaur API key")
    centaur_model_version: str = Field(default="v1", description="Centaur model version")
    centaur_timeout: int = Field(default=30, description="Centaur API timeout")
    centaur_max_retries: int = Field(default=3, description="Max retries for Centaur API")

    # Vector Database Configuration
    vector_db_type: str = Field(default="chroma", description="Vector DB type: chroma, pinecone, weaviate")

    # Chroma
    chroma_persist_directory: str = Field(default="./chroma_db", description="Chroma persistence directory")

    # Pinecone
    pinecone_api_key: Optional[str] = Field(default=None, description="Pinecone API key")
    pinecone_environment: Optional[str] = Field(default=None, description="Pinecone environment")
    pinecone_index_name: str = Field(default="psyai-index", description="Pinecone index name")

    # Weaviate
    weaviate_url: str = Field(default="http://localhost:8080", description="Weaviate URL")
    weaviate_api_key: Optional[str] = Field(default=None, description="Weaviate API key")

    # Embedding Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model",
    )
    embedding_dimension: int = Field(default=384, description="Embedding dimension")

    # RAG Configuration
    rag_chunk_size: int = Field(default=1000, description="RAG chunk size")
    rag_chunk_overlap: int = Field(default=200, description="RAG chunk overlap")
    rag_top_k: int = Field(default=5, description="RAG top K results")
    rag_similarity_threshold: float = Field(default=0.7, description="RAG similarity threshold")

    # Evaluation Configuration
    eval_failure_threshold: float = Field(default=0.7, description="Eval failure threshold")
    eval_auto_trigger: bool = Field(default=True, description="Auto-trigger evals")
    eval_batch_size: int = Field(default=10, description="Eval batch size")

    # Human-in-the-Loop Configuration
    hitl_enabled: bool = Field(default=True, description="Enable HITL")
    hitl_notification_email: Optional[str] = Field(default=None, description="HITL notification email")
    hitl_notification_webhook: Optional[str] = Field(default=None, description="HITL webhook URL")
    hitl_auto_assign: bool = Field(default=True, description="Auto-assign reviews")

    # Confidence Score Configuration
    confidence_min_threshold: float = Field(default=0.6, description="Min confidence threshold")
    confidence_high_threshold: float = Field(default=0.8, description="High confidence threshold")
    confidence_cache_ttl: int = Field(default=3600, description="Confidence cache TTL (seconds)")

    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins",
    )
    cors_allow_credentials: bool = Field(default=True, description="CORS allow credentials")
    cors_allow_methods: List[str] = Field(default=["*"], description="CORS allowed methods")
    cors_allow_headers: List[str] = Field(default=["*"], description="CORS allowed headers")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    rate_limit_per_hour: int = Field(default=1000, description="Rate limit per hour")

    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics")
    metrics_port: int = Field(default=9090, description="Metrics port")
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")
    sentry_environment: Optional[str] = Field(default=None, description="Sentry environment")

    # Development
    seed_database: bool = Field(default=False, description="Seed database on startup")
    seed_admin_email: str = Field(default="admin@example.com", description="Seed admin email")
    seed_admin_password: str = Field(default="admin123", description="Seed admin password")
    enable_debug_toolbar: bool = Field(default=False, description="Enable debug toolbar")

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        """Validate application environment."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v_upper

    @field_validator("vector_db_type")
    @classmethod
    def validate_vector_db_type(cls, v: str) -> str:
        """Validate vector database type."""
        allowed = ["chroma", "pinecone", "weaviate"]
        if v.lower() not in allowed:
            raise ValueError(f"vector_db_type must be one of {allowed}")
        return v.lower()

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"

    @property
    def is_staging(self) -> bool:
        """Check if running in staging mode."""
        return self.app_env == "staging"

    def get_database_url_async(self) -> str:
        """Get async database URL for SQLAlchemy."""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")

    def model_dump_safe(self) -> Dict[str, Any]:
        """
        Dump settings without sensitive information.

        Returns:
            Dict with sensitive fields masked
        """
        data = self.model_dump()

        # Mask sensitive fields
        sensitive_fields = [
            "secret_key",
            "openai_api_key",
            "anthropic_api_key",
            "cohere_api_key",
            "huggingface_api_key",
            "langsmith_api_key",
            "centaur_api_key",
            "pinecone_api_key",
            "weaviate_api_key",
            "sentry_dsn",
            "seed_admin_password",
            "database_url",
        ]

        for field in sensitive_fields:
            if field in data and data[field]:
                data[field] = "***MASKED***"

        return data


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings instance

    Note:
        This is cached to avoid reading .env file multiple times.
        In tests, clear the cache with get_settings.cache_clear()
    """
    return Settings()


# Export singleton instance
settings = get_settings()
