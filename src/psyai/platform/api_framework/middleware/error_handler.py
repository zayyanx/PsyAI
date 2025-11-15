"""
Error handling middleware.

Handles exceptions and returns appropriate HTTP responses.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from psyai.core.exceptions import (
    APIError,
    AuthenticationError,
    CacheError,
    DatabaseError,
    LLMError,
    PsyAIException,
    RateLimitError,
    ValidationError,
)
from psyai.core.logging import get_logger

logger = get_logger(__name__)


def add_error_handlers(app: FastAPI) -> None:
    """
    Add error handlers to FastAPI app.

    Args:
        app: FastAPI application
    """

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        """Handle validation errors."""
        logger.warning(
            "validation_error",
            path=request.url.path,
            error=str(exc),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "message": str(exc),
                "details": exc.details,
            },
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(request: Request, exc: AuthenticationError):
        """Handle authentication errors."""
        logger.warning(
            "authentication_error",
            path=request.url.path,
            error=str(exc),
        )

        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "authentication_error",
                "message": str(exc),
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(RateLimitError)
    async def rate_limit_error_handler(request: Request, exc: RateLimitError):
        """Handle rate limit errors."""
        logger.warning(
            "rate_limit_error",
            path=request.url.path,
            error=str(exc),
        )

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "rate_limit_error",
                "message": str(exc),
            },
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError):
        """Handle database errors."""
        logger.error(
            "database_error",
            path=request.url.path,
            error=str(exc),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "database_error",
                "message": "A database error occurred",
            },
        )

    @app.exception_handler(CacheError)
    async def cache_error_handler(request: Request, exc: CacheError):
        """Handle cache errors."""
        logger.error(
            "cache_error",
            path=request.url.path,
            error=str(exc),
        )

        # Cache errors shouldn't break the request
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "warning": "cache_unavailable",
                "message": "Cache temporarily unavailable, request processed without caching",
            },
        )

    @app.exception_handler(LLMError)
    async def llm_error_handler(request: Request, exc: LLMError):
        """Handle LLM errors."""
        logger.error(
            "llm_error",
            path=request.url.path,
            error=str(exc),
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "llm_error",
                "message": "AI service temporarily unavailable",
            },
        )

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        """Handle generic API errors."""
        logger.error(
            "api_error",
            path=request.url.path,
            error=str(exc),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": exc.code,
                "message": str(exc),
                "details": exc.details,
            },
        )

    @app.exception_handler(PsyAIException)
    async def psyai_error_handler(request: Request, exc: PsyAIException):
        """Handle generic PsyAI errors."""
        logger.error(
            "psyai_error",
            path=request.url.path,
            error=str(exc),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": exc.code,
                "message": str(exc),
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        """Handle unexpected errors."""
        logger.error(
            "unexpected_error",
            path=request.url.path,
            error=str(exc),
            exc_info=True,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
            },
        )
