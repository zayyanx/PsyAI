"""
API routers module.

Provides FastAPI routers for different endpoints.
"""

from psyai.platform.api_framework.routers import auth, chat, health, users

__all__ = [
    "auth",
    "chat",
    "health",
    "users",
]
