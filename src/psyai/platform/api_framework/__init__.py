"""
API Framework for PsyAI.

This module provides the FastAPI application with authentication,
routers, middleware, and WebSocket support.

The API framework includes:
- FastAPI application with lifespan management
- JWT authentication and authorization
- RESTful API routers (health, auth, users, chat)
- WebSocket support for real-time chat
- Middleware (CORS, logging, error handling)
- Pydantic schemas for request/response validation

Example:
    >>> from psyai.platform.api_framework import app
    >>>
    >>> # Run with uvicorn
    >>> # uvicorn psyai.platform.api_framework:app --reload
"""

from psyai.platform.api_framework.app import app, create_app

__all__ = [
    "app",
    "create_app",
]
