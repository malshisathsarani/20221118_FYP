from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class CrisisEvent(Base):
    __tablename__ = "crisis_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=True)

    severity = Column(String, nullable=False)  # mild, moderate, severe, critical
    crisis_score = Column(Float, nullable=False)
    detected_indicators = Column(Text, nullable=True)  # JSON string of indicators

    # Response tracking
    intervention_provided = Column(Text, nullable=True)
    resources_shared = Column(Text, nullable=True)
    follow_up_required = Column(Boolean, default=True)
    resolved = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="crisis_events")
