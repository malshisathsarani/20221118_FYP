from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Profile fields
    avatar_url = Column(String, nullable=True)  # URL or path to profile picture
    phone_number = Column(String, nullable=True)
    bio = Column(Text, nullable=True)

    # Preferences
    notifications_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)

    # Privacy settings
    data_sharing_consent = Column(Boolean, default=False)
    analytics_consent = Column(Boolean, default=False)

    # Relationships
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    crisis_events = relationship("CrisisEvent", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    emergency_contacts = relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
    artworks = relationship("Artwork", back_populates="user", cascade="all, delete-orphan")
