"""
Chat schemas.

Pydantic models for chat-related requests and responses.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from psyai.platform.storage_layer.database.models import ChatMode


class ChatSessionCreate(BaseModel):
    """Chat session creation schema."""

    mode: ChatMode = Field(default=ChatMode.AI, description="Chat mode")
    title: str | None = Field(None, max_length=255, description="Session title")


class ChatSessionResponse(BaseModel):
    """Chat session response schema."""

    id: int
    user_id: int
    mode: ChatMode
    title: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Message creation schema."""

    content: str = Field(..., min_length=1, description="Message content")


class MessageResponse(BaseModel):
    """Message response schema."""

    id: int
    session_id: int
    role: str
    content: str
    confidence_score: float | None
    needs_review: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Chat request schema."""

    session_id: int | None = Field(None, description="Existing session ID")
    message: str = Field(..., min_length=1, description="User message")
    mode: ChatMode = Field(default=ChatMode.AI, description="Chat mode")


class ChatResponse(BaseModel):
    """Chat response schema."""

    session_id: int
    user_message: MessageResponse
    assistant_message: MessageResponse
