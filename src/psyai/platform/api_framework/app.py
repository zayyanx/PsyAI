"""
FastAPI application for PsyAI.

This module creates and configures the FastAPI application.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from psyai.core.config import get_settings
from psyai.core.logging import get_logger
from psyai.platform.api_framework.middleware.error_handler import add_error_handlers
from psyai.platform.api_framework.middleware.logging import LoggingMiddleware
from psyai.platform.api_framework.routers import auth, chat, health, users
from psyai.platform.storage_layer import close_db, init_db

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("application_starting", env=settings.app_env)

    # Initialize database
    try:
        init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_initialization_failed", error=str(e))

    yield

    # Shutdown
    logger.info("application_shutting_down")

    # Close database connections
    try:
        close_db()
        logger.info("database_closed")
    except Exception as e:
        logger.error("database_close_failed", error=str(e))


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="PsyAI API",
        description="API for PsyAI - Agentic workflows with human-in-the-loop",
        version=settings.app_version,
        docs_url="/docs" if settings.app_debug else None,
        redoc_url="/redoc" if settings.app_debug else None,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Logging middleware
    app.add_middleware(LoggingMiddleware)

    # Error handlers
    add_error_handlers(app)

    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])

    logger.info("fastapi_app_created", version=settings.app_version)

    return app


# Create app instance
app = create_app()
