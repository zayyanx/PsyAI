"""
Middleware module for PsyAI API.

Provides logging, error handling, and other middleware.
"""

from psyai.platform.api_framework.middleware.error_handler import add_error_handlers
from psyai.platform.api_framework.middleware.logging import LoggingMiddleware

__all__ = [
    "LoggingMiddleware",
    "add_error_handlers",
]
