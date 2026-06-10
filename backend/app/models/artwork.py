from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Artwork(Base):
    """Model for storing user drawings/artwork"""
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    image_data = Column(Text, nullable=False)  # Base64 encoded PNG image
    thumbnail_data = Column(Text, nullable=True)  # Base64 encoded thumbnail
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="artworks")

    def __repr__(self):
        return f"<Artwork(id={self.id}, user_id={self.user_id}, title={self.title})>"
