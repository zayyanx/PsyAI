"""
API schemas module.

Pydantic models for API requests and responses.
"""

from psyai.platform.api_framework.schemas.auth import (
    Token,
    TokenData,
    UserLogin,
    UserRegister,
)
from psyai.platform.api_framework.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    MessageCreate,
    MessageResponse,
)
from psyai.platform.api_framework.schemas.users import (
    UserCreate,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # Auth
    "UserLogin",
    "UserRegister",
    "Token",
    "TokenData",
    # Users
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # Chat
    "ChatSessionCreate",
    "ChatSessionResponse",
    "MessageCreate",
    "MessageResponse",
    "ChatRequest",
    "ChatResponse",
]
