"""
Chat router.

Handles chat sessions and messages.
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from psyai.core.logging import get_logger
from psyai.platform.api_framework.dependencies import get_current_active_user
from psyai.platform.api_framework.schemas import (
    ChatSessionCreate,
    ChatSessionResponse,
    MessageCreate,
    MessageResponse,
)
from psyai.platform.storage_layer import (
    ChatSessionRepository,
    MessageRepository,
    User,
    get_db,
)

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/sessions",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create chat session",
)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new chat session.

    Args:
        session_data: Session creation data
        current_user: Current user from authentication
        db: Database session

    Returns:
        Created chat session
    """
    session_repo = ChatSessionRepository(db)

    session = session_repo.create(
        user_id=current_user.id,
        mode=session_data.mode,
        title=session_data.title,
        is_active=True,
    )

    logger.info("chat_session_created", session_id=session.id, user_id=current_user.id)

    return session


@router.get(
    "/sessions",
    response_model=list[ChatSessionResponse],
    summary="List user sessions",
)
async def list_chat_sessions(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List chat sessions for current user.

    Args:
        skip: Number of sessions to skip
        limit: Maximum number of sessions to return
        active_only: Only return active sessions
        current_user: Current user from authentication
        db: Database session

    Returns:
        List of chat sessions
    """
    session_repo = ChatSessionRepository(db)

    sessions = session_repo.get_user_sessions(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        active_only=active_only,
    )

    return sessions


@router.get(
    "/sessions/{session_id}",
    response_model=ChatSessionResponse,
    summary="Get chat session",
)
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get chat session by ID.

    Args:
        session_id: Session ID
        current_user: Current user from authentication
        db: Database session

    Returns:
        Chat session

    Raises:
        HTTPException: If session not found or unauthorized
    """
    session_repo = ChatSessionRepository(db)

    session = session_repo.get(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session",
        )

    return session


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Close chat session",
)
async def close_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Close a chat session.

    Args:
        session_id: Session ID
        current_user: Current user from authentication
        db: Database session

    Raises:
        HTTPException: If session not found or unauthorized
    """
    session_repo = ChatSessionRepository(db)

    session = session_repo.get(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session",
        )

    session_repo.close_session(session_id)

    logger.info("chat_session_closed", session_id=session_id, user_id=current_user.id)

    return None


@router.get(
    "/sessions/{session_id}/messages",
    response_model=list[MessageResponse],
    summary="Get session messages",
)
async def get_session_messages(
    session_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get messages for a chat session.

    Args:
        session_id: Session ID
        skip: Number of messages to skip
        limit: Maximum number of messages to return
        current_user: Current user from authentication
        db: Database session

    Returns:
        List of messages

    Raises:
        HTTPException: If session not found or unauthorized
    """
    session_repo = ChatSessionRepository(db)
    message_repo = MessageRepository(db)

    session = session_repo.get(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session",
        )

    messages = message_repo.get_session_messages(
        session_id=session_id,
        skip=skip,
        limit=limit,
    )

    return messages


@router.post(
    "/sessions/{session_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send message",
)
async def send_message(
    session_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Send a message in a chat session.

    Args:
        session_id: Session ID
        message_data: Message creation data
        current_user: Current user from authentication
        db: Database session

    Returns:
        Created message

    Raises:
        HTTPException: If session not found or unauthorized
    """
    session_repo = ChatSessionRepository(db)
    message_repo = MessageRepository(db)

    session = session_repo.get(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session",
        )

    message = message_repo.create(
        session_id=session_id,
        role="user",
        content=message_data.content,
        needs_review=False,
    )

    logger.info("message_sent", message_id=message.id, session_id=session_id)

    return message


@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: int):
    """
    WebSocket endpoint for real-time chat.

    Args:
        websocket: WebSocket connection
        session_id: Chat session ID
    """
    await websocket.accept()

    logger.info("websocket_connected", session_id=session_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            logger.debug("websocket_message_received", session_id=session_id, message=data)

            # Echo back for now (placeholder for actual LLM integration)
            response = f"Echo: {data}"

            await websocket.send_text(response)

    except WebSocketDisconnect:
        logger.info("websocket_disconnected", session_id=session_id)
    except Exception as e:
        logger.error("websocket_error", session_id=session_id, error=str(e))
        await websocket.close()
