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
    app_version: str = Field(default="0.1.0", description="Application version")
    app_env: str = Field(
        default="development", description="Environment: development, staging, production"
    )
    app_debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_reload: bool = Field(default=True, description="Auto-reload for development")
    api_workers: int = Field(default=1, description="Number of workers")

    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production", description="Secret key for JWT"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration")

    # Database Configuration
    database_url: str = Field(
        default="postgresql://psyai_user:psyai_password@localhost:5432/psyai_db",
        description="Database connection URL",
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Max connections beyond pool size")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_max_connections: int = Field(default=10, description="Max Redis connections")

    # Google Cloud / Vertex AI Configuration
    gcp_project_id: Optional[str] = Field(default=None, description="GCP Project ID")
    gcp_location: str = Field(default="us-central1", description="GCP Location/Region")
    gcp_credentials_path: Optional[str] = Field(
        default=None, description="Path to GCP service account JSON"
    )

    # Vertex AI Model Configuration
    vertex_model: str = Field(default="gemini-1.5-pro", description="Vertex AI model name")
    vertex_temperature: float = Field(default=0.7, description="Model temperature")
    vertex_max_tokens: int = Field(default=2048, description="Max output tokens")
    vertex_top_p: float = Field(default=0.95, description="Top-p sampling")
    vertex_top_k: int = Field(default=40, description="Top-k sampling")

    # Vertex AI Embeddings Configuration
    vertex_embedding_model: str = Field(
        default="text-embedding-004", description="Vertex AI embedding model"
    )
    vertex_embedding_dimension: int = Field(default=768, description="Embedding dimension")

    # Vertex AI Evaluation Configuration
    vertex_eval_enabled: bool = Field(default=True, description="Enable Vertex AI evaluation")
    vertex_eval_metrics: List[str] = Field(
        default=["coherence", "fluency", "safety", "groundedness"],
        description="Vertex AI evaluation metrics",
    )

    # Centaur Model Configuration
    centaur_api_key: Optional[str] = Field(default=None, description="Centaur API key")
    centaur_base_url: Optional[str] = Field(default=None, description="Centaur API base URL")
    centaur_model_version: str = Field(default="v1", description="Centaur model version")
    centaur_timeout: int = Field(default=30, description="Centaur API timeout")
    centaur_max_retries: int = Field(default=3, description="Max retries for Centaur API")

    # Lambda Cloud GPU Inference Configuration
    lambda_enabled: bool = Field(default=False, description="Enable Lambda GPU inference routing")
    lambda_cloud_api_key: Optional[str] = Field(default=None, description="Lambda Cloud API key")
    lambda_cloud_base_url: str = Field(
        default="https://cloud.lambda.ai/api/v1",
        description="Lambda Cloud API base URL",
    )
    lambda_instance_name: str = Field(
        default="psyai-gpu-inference",
        description="Name to assign to launched Lambda instances",
    )
    lambda_instance_type: str = Field(
        default="gpu_2x_h100_sxm",
        description="Lambda instance type name for on-demand GPU",
    )
    lambda_region_name: Optional[str] = Field(
        default=None,
        description="Optional Lambda region override for instance launch",
    )
    lambda_ssh_key_names: str = Field(
        default="",
        description="Comma-separated Lambda SSH key names for launch payload",
    )
    lambda_file_system_names: str = Field(
        default="",
        description="Comma-separated Lambda file system names for launch payload",
    )
    lambda_launch_timeout_seconds: int = Field(
        default=600,
        description="Timeout waiting for Lambda instance to become ready",
    )
    lambda_launch_poll_interval_seconds: int = Field(
        default=10,
        description="Polling interval for Lambda instance readiness checks",
    )
    lambda_idle_shutdown_seconds: int = Field(
        default=900,
        description="Idle time before terminating Lambda instance",
    )
    lambda_auto_shutdown_enabled: bool = Field(
        default=True,
        description="Automatically terminate idle Lambda instances",
    )
    lambda_inference_base_url: Optional[str] = Field(
        default=None,
        description="Optional fixed inference URL override (skips auto IP discovery)",
    )
    lambda_inference_scheme: str = Field(
        default="http",
        description="Scheme for instance-local inference endpoint",
    )
    lambda_inference_port: int = Field(default=8000, description="Port for inference service")
    lambda_inference_mode: str = Field(
        default="completion",
        description="Inference payload mode: completion or chat",
    )
    lambda_inference_path: str = Field(
        default="/v1/completions",
        description="OpenAI-compatible inference endpoint path",
    )
    lambda_inference_model: str = Field(
        default="marcelbinz/Llama-3.1-Centaur-70B",
        description="Default model identifier sent to inference endpoint",
    )
    lambda_inference_api_key: Optional[str] = Field(
        default=None,
        description="Optional API key for inference endpoint auth",
    )
    lambda_inference_timeout_seconds: int = Field(
        default=120,
        description="Timeout for inference calls in seconds",
    )

    # Vector Database Configuration
    vector_db_type: str = Field(
        default="vertex-vector-search", description="Vector DB type: vertex-vector-search, chroma"
    )

    # Vertex AI Vector Search
    vertex_index_id: Optional[str] = Field(
        default=None, description="Vertex Vector Search index ID"
    )
    vertex_index_endpoint_id: Optional[str] = Field(
        default=None, description="Vertex Vector Search endpoint ID"
    )
    vertex_deployed_index_id: Optional[str] = Field(default=None, description="Deployed index ID")

    # Chroma (for backward compatibility)
    chroma_persist_directory: str = Field(
        default="./chroma_db", description="Chroma persistence directory"
    )

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
    hitl_notification_email: Optional[str] = Field(
        default=None, description="HITL notification email"
    )
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
        allowed = ["vertex-vector-search", "chroma"]
        if v.lower() not in allowed:
            raise ValueError(f"vector_db_type must be one of {allowed}")
        return v.lower()

    @field_validator("lambda_inference_mode")
    @classmethod
    def validate_lambda_inference_mode(cls, v: str) -> str:
        """Validate Lambda inference mode."""
        allowed = ["completion", "chat"]
        normalized = v.lower().strip()
        if normalized not in allowed:
            raise ValueError(f"lambda_inference_mode must be one of {allowed}")
        return normalized

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
            "gcp_credentials_path",
            "centaur_api_key",
            "lambda_cloud_api_key",
            "lambda_inference_api_key",
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
