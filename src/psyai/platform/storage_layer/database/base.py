"""
Base database models for PsyAI.

This module provides base classes and utilities for all database models.
"""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

Base = declarative_base()


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class BaseModel(Base, TimestampMixin):
    """
    Base model for all database tables.

    Provides:
    - Auto-incrementing integer primary key (id)
    - created_at timestamp
    - updated_at timestamp
    - to_dict() method for serialization
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name (snake_case)."""
        import re

        name = cls.__name__
        # Convert CamelCase to snake_case
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def to_dict(self, exclude: list = None) -> Dict[str, Any]:
        """
        Convert model to dictionary.

        Args:
            exclude: List of field names to exclude

        Returns:
            Dictionary representation of the model
        """
        exclude = exclude or []
        result = {}

        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                # Convert datetime to ISO format
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[column.name] = value

        return result

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}(id={self.id})>"
