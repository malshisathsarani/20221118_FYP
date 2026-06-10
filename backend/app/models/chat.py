from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, index=True, nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)

    # Emotion analysis
    detected_emotion = Column(String, nullable=True)
    emotion_confidence = Column(Float, nullable=True)
    emotion_scores = Column(JSON, nullable=True)  # All emotion scores

    # Voice analysis (if applicable)
    audio_emotion = Column(String, nullable=True)
    audio_confidence = Column(Float, nullable=True)

    # Crisis detection
    crisis_score = Column(Float, default=0.0)
    is_crisis = Column(Integer, default=0)  # 0: no, 1: mild, 2: moderate, 3: severe

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chats")
