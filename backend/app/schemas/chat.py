from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: str
    audio_data: Optional[str] = None  # Base64 encoded audio


class EmotionAnalysis(BaseModel):
    emotion: str
    confidence: float
    all_scores: Dict[str, float]


class CrisisDetection(BaseModel):
    is_crisis: bool
    severity: Optional[str] = None  # mild, moderate, severe, critical
    crisis_score: float
    indicators: Optional[list[str]] = None


class ChatResponse(BaseModel):
    id: int
    session_id: str
    message: str
    response: str
    emotion_analysis: Optional[EmotionAnalysis] = None
    audio_emotion: Optional[str] = None
    crisis_detection: Optional[CrisisDetection] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    chats: list[ChatResponse]
    total: int
    session_id: Optional[str] = None
