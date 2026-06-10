from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from ...core.database import get_db
from ...schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from ...services.chat_service import ChatService
from ..dependencies import get_current_user_id

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_chat_session(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new chat session.

    Endpoint: POST /api/chat/create

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - session_id: Unique identifier for the new chat session
    - message: Success message
    """
    chat_service = ChatService(db)
    session_id = chat_service.create_session(user_id)

    return {
        "session_id": session_id,
        "user_id": user_id,
        "message": "Chat session created successfully"
    }


@router.post("/{session_id}/message", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    session_id: str,
    chat_request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Send a message in a chat session.

    Endpoint: POST /api/chat/{session_id}/message

    Headers:
    - Authorization: Bearer <access_token>

    Request Body:
    - message: The text message to send
    - session_id: The session ID (also in URL)
    - audio_data: Optional base64 encoded audio

    Returns:
    - ChatResponse with AI response, emotion analysis, and crisis detection
    """
    # Override session_id from path parameter
    chat_request.session_id = session_id

    chat_service = ChatService(db)
    return chat_service.process_message(user_id, chat_request)


@router.get("/{session_id}/messages", response_model=ChatHistoryResponse)
def get_chat_messages(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all messages in a specific chat session.

    Endpoint: GET /api/chat/{session_id}/messages

    Headers:
    - Authorization: Bearer <access_token>

    Query Parameters:
    - limit: Maximum number of messages to return (default: 50, max: 100)
    - offset: Number of messages to skip (for pagination)

    Returns:
    - List of messages with emotion analysis and crisis detection
    """
    if limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit cannot exceed 100"
        )

    chat_service = ChatService(db)
    return chat_service.get_chat_history(user_id, session_id, limit)


@router.get("/my-chats")
def get_my_chats(
    limit: int = 20,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    List all chat sessions for the current user.

    Endpoint: GET /api/chat/my-chats

    Headers:
    - Authorization: Bearer <access_token>

    Query Parameters:
    - limit: Maximum number of sessions to return (default: 20)

    Returns:
    - List of session IDs with metadata
    - Total session count
    """
    chat_service = ChatService(db)
    sessions = chat_service.get_user_sessions(user_id)

    # Get info for each session
    session_details = []
    for session_id in sessions[:limit]:
        try:
            info = chat_service.get_session_info(session_id, user_id)
            session_details.append(info)
        except Exception:
            # Skip sessions with errors
            continue

    return {
        "sessions": session_details,
        "total": len(sessions)
    }


# Additional helpful endpoints

@router.get("/sessions/{session_id}/info")
def get_session_info(
    session_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific session.

    Endpoint: GET /api/chat/sessions/{session_id}/info

    Returns session metadata including:
    - Message count
    - Dominant emotion
    - Crisis alerts count
    - First and last message timestamps
    """
    chat_service = ChatService(db)
    return chat_service.get_session_info(session_id, user_id)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a chat session and all its messages.

    Endpoint: DELETE /api/chat/sessions/{session_id}

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - 204 No Content on success
    """
    chat_service = ChatService(db)
    chat_service.delete_session(session_id, user_id)
    return None


@router.get("/history", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: Optional[str] = None,
    limit: int = 50,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get chat history for the current user.

    Endpoint: GET /api/chat/history

    Query Parameters:
    - session_id: Optional - Filter by specific session
    - limit: Maximum messages to return (default: 50, max: 100)

    Returns:
    - Chat history with all messages
    """
    if limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit cannot exceed 100"
        )

    chat_service = ChatService(db)
    return chat_service.get_chat_history(user_id, session_id, limit)


@router.get("/sessions")
def get_user_sessions(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all session IDs for the current user.

    Endpoint: GET /api/chat/sessions

    Returns:
    - List of all session IDs
    - Total count
    """
    chat_service = ChatService(db)
    sessions = chat_service.get_user_sessions(user_id)
    return {"sessions": sessions, "total": len(sessions)}
