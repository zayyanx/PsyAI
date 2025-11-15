"""
Authentication router.

Handles user registration and login.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from psyai.core.config import get_settings
from psyai.core.logging import get_logger
from psyai.platform.api_framework.auth import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from psyai.platform.api_framework.schemas import Token, UserLogin, UserRegister, UserResponse
from psyai.platform.storage_layer import UserRepository, get_db

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user

    Raises:
        HTTPException: If email or username already exists
    """
    user_repo = UserRepository(db)

    # Check if email exists
    if user_repo.get_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username exists
    if user_repo.get_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create user
    hashed_password = get_password_hash(user_data.password)

    user = user_repo.create(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_expert=False,
        is_admin=False,
    )

    logger.info("user_registered", user_id=user.id, email=user.email)

    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login user",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login user and get access token.

    Args:
        form_data: Login form data (username/email and password)
        db: Database session

    Returns:
        Access token

    Raises:
        HTTPException: If credentials are invalid
    """
    user_repo = UserRepository(db)

    # Try to find user by email or username
    user = user_repo.get_by_email(form_data.username)
    if not user:
        user = user_repo.get_by_username(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires,
    )

    logger.info("user_logged_in", user_id=user.id, email=user.email)

    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/login/json",
    response_model=Token,
    summary="Login user (JSON)",
)
async def login_json(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Login user with JSON body.

    Args:
        user_data: User login data
        db: Database session

    Returns:
        Access token

    Raises:
        HTTPException: If credentials are invalid
    """
    user_repo = UserRepository(db)

    # Find user by email
    user = user_repo.get_by_email(user_data.email)

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires,
    )

    logger.info("user_logged_in_json", user_id=user.id, email=user.email)

    return Token(access_token=access_token, token_type="bearer")
