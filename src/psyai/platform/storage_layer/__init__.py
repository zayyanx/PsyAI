"""
Storage Layer for PsyAI.

This module provides database models, caching, and data access patterns.

The storage layer includes:
- Database models (SQLAlchemy ORM)
- Session management (connection pooling, transactions)
- Redis caching (sync and async)
- Repository patterns (CRUD operations)

Example:
    >>> from psyai.platform.storage_layer import (
    ...     get_db,
    ...     UserRepository,
    ...     get_redis_client,
    ... )
    >>>
    >>> # Database
    >>> with get_db_context() as db:
    ...     user_repo = UserRepository(db)
    ...     user = user_repo.create(
    ...         email="test@example.com",
    ...         username="test",
    ...         hashed_password="...",
    ...     )
    >>>
    >>> # Cache
    >>> cache = get_redis_client()
    >>> cache.set("key", {"data": "value"}, ttl=3600)
    >>> result = cache.get("key")
"""

# Database
from psyai.platform.storage_layer.database import (
    Base,
    BaseModel,
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
    TimestampMixin,
    User,
    close_db,
    create_database_engine,
    drop_db,
    get_db,
    get_db_context,
    get_engine,
    get_session_factory,
    init_db,
)

# Cache
from psyai.platform.storage_layer.cache import RedisClient, get_redis_client

# Repositories
from psyai.platform.storage_layer.repositories import (
    BaseRepository,
    ChatSessionRepository,
    MessageRepository,
    UserRepository,
)

__all__ = [
    # Database - Base
    "Base",
    "BaseModel",
    "TimestampMixin",
    # Database - Models
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
    # Database - Enums
    "ChatMode",
    "ReviewStatus",
    # Database - Session
    "get_engine",
    "get_session_factory",
    "get_db",
    "get_db_context",
    "create_database_engine",
    "init_db",
    "drop_db",
    "close_db",
    # Cache
    "RedisClient",
    "get_redis_client",
    # Repositories
    "BaseRepository",
    "UserRepository",
    "ChatSessionRepository",
    "MessageRepository",
]
