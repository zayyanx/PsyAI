"""
Health check router.

Provides health check endpoints for monitoring.
"""

from fastapi import APIRouter, status
from pydantic import BaseModel

from psyai.core.config import get_settings
from psyai.core.logging import get_logger
from psyai.platform.storage_layer import get_redis_client

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    environment: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response."""

    status: str
    version: str
    environment: str
    database: str
    cache: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
)
async def health_check():
    """
    Basic health check endpoint.

    Returns:
        Health status
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.app_env,
    )


@router.get(
    "/health/detailed",
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Detailed health check",
)
async def detailed_health_check():
    """
    Detailed health check with dependency status.

    Returns:
        Detailed health status including database and cache
    """
    # Check database
    db_status = "healthy"
    try:
        from psyai.platform.storage_layer import get_engine

        engine = get_engine()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        db_status = "unhealthy"

    # Check cache
    cache_status = "healthy"
    try:
        cache = get_redis_client()
        cache.ping()
    except Exception as e:
        logger.error("cache_health_check_failed", error=str(e))
        cache_status = "unhealthy"

    return DetailedHealthResponse(
        status="healthy" if db_status == "healthy" and cache_status == "healthy" else "degraded",
        version=settings.app_version,
        environment=settings.app_env,
        database=db_status,
        cache=cache_status,
    )


@router.get(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Ping endpoint",
)
async def ping():
    """
    Simple ping endpoint.

    Returns:
        Pong response
    """
    return {"message": "pong"}
