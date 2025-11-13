"""
Chat repository.

This module provides database operations for Chat-related models.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from psyai.core.logging import get_logger
from psyai.platform.storage_layer.database.models import ChatMode, ChatSession, Message
from psyai.platform.storage_layer.repositories.base import BaseRepository

logger = get_logger(__name__)


class ChatSessionRepository(BaseRepository[ChatSession]):
    """
    Repository for ChatSession model.

    Provides chat session-specific database operations.
    """

    def __init__(self, db: Session):
        """Initialize chat session repository."""
        super().__init__(ChatSession, db)

    def get_user_sessions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> List[ChatSession]:
        """
        Get chat sessions for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records
            active_only: Only return active sessions

        Returns:
            List of chat sessions
        """
        if active_only:
            return self.get_all(skip=skip, limit=limit, user_id=user_id, is_active=True)
        return self.get_all(skip=skip, limit=limit, user_id=user_id)

    def get_by_mode(
        self,
        user_id: int,
        mode: ChatMode,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChatSession]:
        """
        Get chat sessions by mode.

        Args:
            user_id: User ID
            mode: Chat mode
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of chat sessions
        """
        return self.get_all(skip=skip, limit=limit, user_id=user_id, mode=mode)

    def close_session(self, session_id: int) -> Optional[ChatSession]:
        """
        Close a chat session.

        Args:
            session_id: Session ID

        Returns:
            Updated session or None
        """
        return self.update(session_id, is_active=False)

    def reopen_session(self, session_id: int) -> Optional[ChatSession]:
        """
        Reopen a chat session.

        Args:
            session_id: Session ID

        Returns:
            Updated session or None
        """
        return self.update(session_id, is_active=True)


class MessageRepository(BaseRepository[Message]):
    """
    Repository for Message model.

    Provides message-specific database operations.
    """

    def __init__(self, db: Session):
        """Initialize message repository."""
        super().__init__(Message, db)

    def get_session_messages(
        self,
        session_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Message]:
        """
        Get messages for a session.

        Args:
            session_id: Session ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of messages ordered by creation time
        """
        messages = (
            self.db.query(self.model)
            .filter(self.model.session_id == session_id)
            .order_by(self.model.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        logger.debug(
            "repository_get_session_messages",
            session_id=session_id,
            count=len(messages),
        )

        return messages

    def get_messages_needing_review(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Message]:
        """
        Get messages that need review.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of messages needing review
        """
        return self.get_all(skip=skip, limit=limit, needs_review=True)

    def flag_for_review(self, message_id: int) -> Optional[Message]:
        """
        Flag a message for review.

        Args:
            message_id: Message ID

        Returns:
            Updated message or None
        """
        return self.update(message_id, needs_review=True)

    def unflag_for_review(self, message_id: int) -> Optional[Message]:
        """
        Unflag a message from review.

        Args:
            message_id: Message ID

        Returns:
            Updated message or None
        """
        return self.update(message_id, needs_review=False)
