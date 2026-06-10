from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=True)

    rating = Column(Integer, nullable=False)  # 1-5 stars
    feedback_type = Column(String, nullable=False)  # emotion_accuracy, response_quality, crisis_detection
    comment = Column(Text, nullable=True)

    is_processed = Column(Boolean, default=False)  # For bias detection/model improvement
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="feedback")
