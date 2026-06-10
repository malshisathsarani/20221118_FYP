from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MessageBase(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: str


class MessageCreate(MessageBase):
    audio_data: Optional[str] = None  # Base64 encoded audio
    audio_url: Optional[str] = None   # URL to uploaded audio file


class MessageResponse(MessageBase):
    id: int
    user_id: int
    response: str
    audio_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MessageWithEmotionResponse(MessageResponse):
    """Message response with embedded emotion analysis"""
    detected_emotion: Optional[str] = None
    emotion_confidence: Optional[float] = None
    audio_emotion: Optional[str] = None
    audio_confidence: Optional[float] = None
    crisis_score: Optional[float] = None
    is_crisis: Optional[int] = None

    class Config:
        from_attributes = True
