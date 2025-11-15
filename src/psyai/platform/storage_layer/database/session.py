"""
Database session management.

This module provides database connection and session management.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from psyai.core.config import get_settings
from psyai.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


# Global engine and session factory
_engine: Engine = None
_SessionLocal: sessionmaker = None


def create_database_engine(
    database_url: str = None,
    echo: bool = False,
    pool_size: int = None,
    max_overflow: int = None,
    pool_pre_ping: bool = True,
) -> Engine:
    """
    Create SQLAlchemy engine.

    Args:
        database_url: Database connection URL
        echo: Whether to log SQL statements
        pool_size: Connection pool size
        max_overflow: Max connections beyond pool_size
        pool_pre_ping: Enable connection health checks

    Returns:
        SQLAlchemy Engine instance
    """
    database_url = database_url or settings.database_url
    echo = echo if echo is not None else settings.app_debug
    pool_size = pool_size or settings.database_pool_size or 5
    max_overflow = max_overflow or settings.database_max_overflow or 10

    logger.info(
        "creating_database_engine",
        database_url=database_url.split("@")[-1] if "@" in database_url else database_url,  # Hide credentials
        pool_size=pool_size,
        max_overflow=max_overflow,
    )

    # Determine if we should use a connection pool
    # SQLite doesn't support connection pooling
    if database_url.startswith("sqlite"):
        poolclass = NullPool
        connect_args = {"check_same_thread": False}
        engine = create_engine(
            database_url,
            echo=echo,
            poolclass=poolclass,
            connect_args=connect_args,
        )
    else:
        poolclass = QueuePool
        engine = create_engine(
            database_url,
            echo=echo,
            poolclass=poolclass,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping,
        )

    # Add event listeners for connection management
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Called when a connection is created."""
        logger.debug("database_connection_created")

    @event.listens_for(engine, "close")
    def receive_close(dbapi_conn, connection_record):
        """Called when a connection is closed."""
        logger.debug("database_connection_closed")

    return engine


def get_engine() -> Engine:
    """
    Get or create the global database engine.

    Returns:
        SQLAlchemy Engine instance
    """
    global _engine

    if _engine is None:
        _engine = create_database_engine()

    return _engine


def get_session_factory() -> sessionmaker:
    """
    Get or create the global session factory.

    Returns:
        SQLAlchemy sessionmaker
    """
    global _SessionLocal

    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
        logger.info("session_factory_created")

    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database sessions.

    Yields:
        Database session

    Example:
        >>> from fastapi import Depends
        >>> @app.get("/users")
        >>> def get_users(db: Session = Depends(get_db)):
        ...     return db.query(User).all()
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Yields:
        Database session

    Example:
        >>> with get_db_context() as db:
        ...     user = db.query(User).first()
        ...     print(user.email)
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database (create all tables).

    This should be called on application startup.
    """
    from psyai.platform.storage_layer.database.base import Base
    from psyai.platform.storage_layer.database.models import (
        User,
        ChatSession,
        Message,
        Review,
        Dataset,
        DatasetExample,
        Evaluation,
        EvaluationResult,
        Document,
        DocumentChunk,
    )

    engine = get_engine()

    logger.info("initializing_database", tables=len(Base.metadata.tables))
    Base.metadata.create_all(bind=engine)
    logger.info("database_initialized", tables=list(Base.metadata.tables.keys()))


def drop_db() -> None:
    """
    Drop all database tables.

    WARNING: This will delete all data!
    Only use in development/testing.
    """
    from psyai.platform.storage_layer.database.base import Base

    engine = get_engine()

    if settings.app_env == "production":
        raise RuntimeError("Cannot drop database in production!")

    logger.warning("dropping_all_database_tables")
    Base.metadata.drop_all(bind=engine)
    logger.info("database_dropped")


def close_db() -> None:
    """Close database connections."""
    global _engine, _SessionLocal

    if _engine:
        _engine.dispose()
        _engine = None
        logger.info("database_engine_disposed")

    _SessionLocal = None
