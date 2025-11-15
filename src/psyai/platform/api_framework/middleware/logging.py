"""
Logging middleware.

Logs all HTTP requests and responses.
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from psyai.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log HTTP requests and responses.

    Logs request method, path, status code, and duration.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """
        Process request and log details.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        start_time = time.time()

        # Get request details
        method = request.method
        path = request.url.path
        client = request.client.host if request.client else "unknown"

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log request
        logger.info(
            "http_request",
            method=method,
            path=path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
            client=client,
        )

        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)

        return response
