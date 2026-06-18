from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class GameSession(Base):
    """Model for tracking wellness game/tool sessions"""
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Game info
    game_type = Column(String, nullable=False)  # 'breathing', 'puzzle', 'drawing', 'coloring'
    game_name = Column(String, nullable=False)  # Display name

    # Session timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    completed = Column(Boolean, default=False)

    # Mood tracking (optional)
    pre_mood = Column(Integer, nullable=True)  # 1-5 scale
    post_mood = Column(Integer, nullable=True)  # 1-5 scale
    mood_improvement = Column(Float, nullable=True)  # Calculated: post - pre

    # Effectiveness
    effectiveness_rating = Column(Integer, nullable=True)  # 1-5 stars
    notes = Column(String, nullable=True)

    # Metadata
    device = Column(String, nullable=True)  # 'mobile', 'web'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="game_sessions")


class UserAchievement(Base):
    """Model for tracking user achievements and milestones"""
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Achievement info
    achievement_type = Column(String, nullable=False)  # 'streak_7', 'breathing_25', etc.
    achievement_name = Column(String, nullable=False)  # Display name
    achievement_description = Column(String, nullable=True)

    # Status
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    progress = Column(Integer, default=0)  # Current progress
    target = Column(Integer, nullable=True)  # Target to unlock

    # Metadata
    icon = Column(String, nullable=True)  # Icon name
    category = Column(String, nullable=True)  # 'consistency', 'activity', 'mood', 'time'

    # Relationship
    user = relationship("User", back_populates="achievements")
