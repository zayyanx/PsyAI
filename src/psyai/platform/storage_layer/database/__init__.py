"""
Database module for PsyAI storage layer.

This module provides database models, session management, and utilities.
"""

from psyai.platform.storage_layer.database.base import Base, BaseModel, TimestampMixin
from psyai.platform.storage_layer.database.models import (
    ChatMode,
    ChatSession,
    Dataset,
    DatasetExample,
    Document,
    DocumentChunk,
    Evaluation,
    EvaluationResult,
    Message,
    Review,
    ReviewStatus,
    User,
)
from psyai.platform.storage_layer.database.session import (
    close_db,
    create_database_engine,
    drop_db,
    get_db,
    get_db_context,
    get_engine,
    get_session_factory,
    init_db,
)

__all__ = [
    # Base
    "Base",
    "BaseModel",
    "TimestampMixin",
    # Models
    "User",
    "ChatSession",
    "Message",
    "Review",
    "Dataset",
    "DatasetExample",
    "Evaluation",
    "EvaluationResult",
    "Document",
    "DocumentChunk",
    # Enums
    "ChatMode",
    "ReviewStatus",
    # Session
    "get_engine",
    "get_session_factory",
    "get_db",
    "get_db_context",
    "create_database_engine",
    "init_db",
    "drop_db",
    "close_db",
]
