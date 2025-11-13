"""
User repository.

This module provides database operations for User model.
"""

from typing import Optional

from sqlalchemy.orm import Session

from psyai.core.logging import get_logger
from psyai.platform.storage_layer.database.models import User
from psyai.platform.storage_layer.repositories.base import BaseRepository

logger = get_logger(__name__)


class UserRepository(BaseRepository[User]):
    """
    Repository for User model.

    Provides user-specific database operations.
    """

    def __init__(self, db: Session):
        """Initialize user repository."""
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User instance or None
        """
        return self.get_by(email=email)

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: Username

        Returns:
            User instance or None
        """
        return self.get_by(username=username)

    def get_experts(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Get all expert users.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of expert users
        """
        return self.get_all(skip=skip, limit=limit, is_expert=True)

    def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Get all active users.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of active users
        """
        return self.get_all(skip=skip, limit=limit, is_active=True)

    def deactivate(self, id: int) -> Optional[User]:
        """
        Deactivate a user.

        Args:
            id: User ID

        Returns:
            Updated user or None
        """
        return self.update(id, is_active=False)

    def activate(self, id: int) -> Optional[User]:
        """
        Activate a user.

        Args:
            id: User ID

        Returns:
            Updated user or None
        """
        return self.update(id, is_active=True)
