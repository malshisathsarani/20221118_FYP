from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from ..models.chat import Chat


class MessageRepository:
    """
    Repository for Message database operations.

    Note: Since we use a consolidated Chat model that combines messages,
    this repository provides message-specific operations on the Chat table.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_message(
        self,
        user_id: int,
        session_id: str,
        message: str,
        response: str,
        audio_url: Optional[str] = None
    ) -> Chat:
        """Create a new message (chat entry)"""
        chat = Chat(
            user_id=user_id,
            session_id=session_id,
            message=message,
            response=response
        )
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_message_by_id(self, message_id: int) -> Optional[Chat]:
        """Get a single message by ID"""
        return self.db.query(Chat).filter(Chat.id == message_id).first()

    def get_messages_by_session(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Chat]:
        """Get all messages in a chat session"""
        return (
            self.db.query(Chat)
            .filter(Chat.session_id == session_id)
            .order_by(Chat.created_at.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_messages_by_user(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Chat]:
        """Get all messages for a specific user"""
        return (
            self.db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(Chat.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_recent_messages(
        self,
        user_id: int,
        session_id: str,
        limit: int = 10
    ) -> List[Chat]:
        """Get recent messages in a session for context"""
        return (
            self.db.query(Chat)
            .filter(
                Chat.user_id == user_id,
                Chat.session_id == session_id
            )
            .order_by(Chat.created_at.desc())
            .limit(limit)
            .all()
        )

    def update_message_emotion(
        self,
        message_id: int,
        detected_emotion: str,
        emotion_confidence: float,
        emotion_scores: Optional[dict] = None
    ) -> Optional[Chat]:
        """Update emotion analysis for a message"""
        message = self.get_message_by_id(message_id)
        if message:
            message.detected_emotion = detected_emotion
            message.emotion_confidence = emotion_confidence
            message.emotion_scores = emotion_scores
            self.db.commit()
            self.db.refresh(message)
        return message

    def update_message_audio_emotion(
        self,
        message_id: int,
        audio_emotion: str,
        audio_confidence: float
    ) -> Optional[Chat]:
        """Update audio emotion analysis for a message"""
        message = self.get_message_by_id(message_id)
        if message:
            message.audio_emotion = audio_emotion
            message.audio_confidence = audio_confidence
            self.db.commit()
            self.db.refresh(message)
        return message

    def update_message_crisis_score(
        self,
        message_id: int,
        crisis_score: float,
        is_crisis: int
    ) -> Optional[Chat]:
        """Update crisis detection score for a message"""
        message = self.get_message_by_id(message_id)
        if message:
            message.crisis_score = crisis_score
            message.is_crisis = is_crisis
            self.db.commit()
            self.db.refresh(message)
        return message

    def delete_message(self, message_id: int) -> bool:
        """Delete a message"""
        message = self.get_message_by_id(message_id)
        if message:
            self.db.delete(message)
            self.db.commit()
            return True
        return False

    def count_messages_in_session(self, session_id: str) -> int:
        """Count total messages in a session"""
        return self.db.query(Chat).filter(Chat.session_id == session_id).count()

    def count_user_messages(self, user_id: int) -> int:
        """Count total messages for a user"""
        return self.db.query(Chat).filter(Chat.user_id == user_id).count()

    def search_messages(
        self,
        user_id: int,
        search_term: str,
        limit: int = 50
    ) -> List[Chat]:
        """Search messages by content"""
        return (
            self.db.query(Chat)
            .filter(
                Chat.user_id == user_id,
                Chat.message.contains(search_term)
            )
            .order_by(Chat.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_messages_by_emotion(
        self,
        user_id: int,
        emotion: str,
        limit: int = 50
    ) -> List[Chat]:
        """Get messages by detected emotion"""
        return (
            self.db.query(Chat)
            .filter(
                Chat.user_id == user_id,
                Chat.detected_emotion == emotion
            )
            .order_by(Chat.created_at.desc())
            .limit(limit)
            .all()
        )
