"""
Base repository for database operations.

This module provides a generic repository pattern for all models.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from psyai.core.logging import get_logger
from psyai.platform.storage_layer.database.base import BaseModel

logger = get_logger(__name__)

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository for database operations.

    Provides common CRUD operations for any model.

    Example:
        >>> class UserRepository(BaseRepository[User]):
        ...     pass
        >>> repo = UserRepository(User, db_session)
        >>> user = repo.create(email="test@example.com", username="test")
    """

    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    def create(self, **kwargs) -> ModelType:
        """
        Create a new record.

        Args:
            **kwargs: Model fields

        Returns:
            Created model instance
        """
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)

        logger.info(
            "repository_create",
            model=self.model.__name__,
            id=instance.id,
        )

        return instance

    def get(self, id: int) -> Optional[ModelType]:
        """
        Get record by ID.

        Args:
            id: Record ID

        Returns:
            Model instance or None
        """
        instance = self.db.query(self.model).filter(self.model.id == id).first()

        if instance:
            logger.debug("repository_get_found", model=self.model.__name__, id=id)
        else:
            logger.debug("repository_get_not_found", model=self.model.__name__, id=id)

        return instance

    def get_by(self, **filters) -> Optional[ModelType]:
        """
        Get single record by filters.

        Args:
            **filters: Field filters

        Returns:
            Model instance or None
        """
        query = self.db.query(self.model)

        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)

        instance = query.first()

        if instance:
            logger.debug("repository_get_by_found", model=self.model.__name__, filters=filters)
        else:
            logger.debug("repository_get_by_not_found", model=self.model.__name__, filters=filters)

        return instance

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters,
    ) -> List[ModelType]:
        """
        Get all records with optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Field filters

        Returns:
            List of model instances
        """
        query = self.db.query(self.model)

        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)

        instances = query.offset(skip).limit(limit).all()

        logger.debug(
            "repository_get_all",
            model=self.model.__name__,
            count=len(instances),
            skip=skip,
            limit=limit,
        )

        return instances

    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        Update a record.

        Args:
            id: Record ID
            **kwargs: Fields to update

        Returns:
            Updated model instance or None
        """
        instance = self.get(id)

        if not instance:
            logger.warning("repository_update_not_found", model=self.model.__name__, id=id)
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self.db.commit()
        self.db.refresh(instance)

        logger.info("repository_update", model=self.model.__name__, id=id)

        return instance

    def delete(self, id: int) -> bool:
        """
        Delete a record.

        Args:
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        instance = self.get(id)

        if not instance:
            logger.warning("repository_delete_not_found", model=self.model.__name__, id=id)
            return False

        self.db.delete(instance)
        self.db.commit()

        logger.info("repository_delete", model=self.model.__name__, id=id)

        return True

    def count(self, **filters) -> int:
        """
        Count records with optional filters.

        Args:
            **filters: Field filters

        Returns:
            Number of records
        """
        query = self.db.query(self.model)

        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)

        count = query.count()

        logger.debug("repository_count", model=self.model.__name__, count=count)

        return count

    def exists(self, id: int) -> bool:
        """
        Check if record exists.

        Args:
            id: Record ID

        Returns:
            True if exists, False otherwise
        """
        exists = self.db.query(self.model.id).filter(self.model.id == id).first() is not None

        logger.debug("repository_exists", model=self.model.__name__, id=id, exists=exists)

        return exists
