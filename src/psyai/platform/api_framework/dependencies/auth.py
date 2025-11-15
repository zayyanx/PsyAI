"""
Authentication dependencies.

FastAPI dependencies for authentication and authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from psyai.core.logging import get_logger
from psyai.platform.api_framework.auth import decode_access_token
from psyai.platform.storage_layer import User, UserRepository, get_db

logger = get_logger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If user not found or inactive
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id: int = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    # Get user from database
    user_repo = UserRepository(db)
    user = user_repo.get(user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    logger.debug("current_user_retrieved", user_id=user.id, email=user.email)

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (alias for get_current_user).

    Args:
        current_user: Current user from get_current_user

    Returns:
        Active user
    """
    return current_user


async def get_current_expert(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current expert user.

    Args:
        current_user: Current user from get_current_user

    Returns:
        Expert user

    Raises:
        HTTPException: If user is not an expert
    """
    if not current_user.is_expert:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Expert privileges required",
        )

    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current admin user.

    Args:
        current_user: Current user from get_current_user

    Returns:
        Admin user

    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    return current_user
