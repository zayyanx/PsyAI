"""
Authentication schemas.

Pydantic models for authentication requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    """User login request."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")


class UserRegister(BaseModel):
    """User registration request."""

    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    password: str = Field(..., min_length=8, description="Password")
    full_name: str | None = Field(None, max_length=255, description="Full name")


class Token(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Token payload data."""

    user_id: int | None = None
    email: str | None = None
