"""
Users router.

Handles user management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from psyai.core.logging import get_logger
from psyai.platform.api_framework.dependencies import get_current_active_user, get_current_admin
from psyai.platform.api_framework.schemas import UserResponse, UserUpdate
from psyai.platform.storage_layer import User, UserRepository, get_db

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current authenticated user's information.

    Args:
        current_user: Current user from authentication

    Returns:
        User information
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's information.

    Args:
        user_update: User update data
        current_user: Current user from authentication
        db: Database session

    Returns:
        Updated user
    """
    user_repo = UserRepository(db)

    update_data = user_update.model_dump(exclude_unset=True)

    updated_user = user_repo.update(current_user.id, **update_data)

    logger.info("user_updated", user_id=current_user.id)

    return updated_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get user by ID.

    Args:
        user_id: User ID
        db: Database session
        current_user: Current user from authentication

    Returns:
        User information

    Raises:
        HTTPException: If user not found
    """
    user_repo = UserRepository(db)

    user = user_repo.get(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="List users",
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),  # Only admins can list all users
):
    """
    List all users (admin only).

    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        db: Database session
        current_user: Current admin user

    Returns:
        List of users
    """
    user_repo = UserRepository(db)

    users = user_repo.get_all(skip=skip, limit=limit)

    return users


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),  # Only admins can delete users
):
    """
    Delete user (admin only).

    Args:
        user_id: User ID to delete
        db: Database session
        current_user: Current admin user

    Raises:
        HTTPException: If user not found
    """
    user_repo = UserRepository(db)

    if not user_repo.delete(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    logger.info("user_deleted", user_id=user_id, deleted_by=current_user.id)

    return None
