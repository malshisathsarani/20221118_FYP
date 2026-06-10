from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from ..models.chat import Chat


class ChatRepository:
    """Repository for Chat database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        session_id: str,
        message: str,
        response: str,
        detected_emotion: Optional[str] = None,
        emotion_confidence: Optional[float] = None,
        emotion_scores: Optional[dict] = None,
        audio_emotion: Optional[str] = None,
        audio_confidence: Optional[float] = None,
        crisis_score: float = 0.0,
        is_crisis: int = 0
    ) -> Chat:
        """Create a new chat entry"""
        chat = Chat(
            user_id=user_id,
            session_id=session_id,
            message=message,
            response=response,
            detected_emotion=detected_emotion,
            emotion_confidence=emotion_confidence,
            emotion_scores=emotion_scores,
            audio_emotion=audio_emotion,
            audio_confidence=audio_confidence,
            crisis_score=crisis_score,
            is_crisis=is_crisis
        )
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_by_id(self, chat_id: int) -> Optional[Chat]:
        """Get chat by ID"""
        return self.db.query(Chat).filter(Chat.id == chat_id).first()

    def get_by_session(self, session_id: str, limit: int = 50) -> List[Chat]:
        """Get all chats in a session"""
        return (
            self.db.query(Chat)
            .filter(Chat.session_id == session_id)
            .order_by(Chat.created_at.asc())
            .limit(limit)
            .all()
        )

    def get_by_user(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Chat]:
        """Get all chats for a user"""
        return (
            self.db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(Chat.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_user_sessions(self, user_id: int) -> List[str]:
        """Get all unique session IDs for a user"""
        sessions = (
            self.db.query(Chat.session_id)
            .filter(Chat.user_id == user_id)
            .distinct()
            .all()
        )
        return [session[0] for session in sessions]

    def get_crisis_chats(self, user_id: int) -> List[Chat]:
        """Get all chats with crisis detection"""
        return (
            self.db.query(Chat)
            .filter(Chat.user_id == user_id, Chat.is_crisis > 0)
            .order_by(Chat.created_at.desc())
            .all()
        )

    def count_user_chats(self, user_id: int) -> int:
        """Count total chats for a user"""
        return self.db.query(Chat).filter(Chat.user_id == user_id).count()
