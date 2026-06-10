from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime


class EmotionScores(BaseModel):
    """Individual emotion scores"""
    joy: Optional[float] = None
    sadness: Optional[float] = None
    anger: Optional[float] = None
    fear: Optional[float] = None
    surprise: Optional[float] = None
    disgust: Optional[float] = None
    neutral: Optional[float] = None


class TextEmotionAnalysis(BaseModel):
    """Text-based emotion analysis result"""
    emotion: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    all_scores: Dict[str, float]


class VoiceEmotionAnalysis(BaseModel):
    """Voice-based emotion analysis result"""
    emotion: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    all_scores: Optional[Dict[str, float]] = None


class EmotionAnalysisResponse(BaseModel):
    """Complete emotion analysis response"""
    text_emotion: Optional[TextEmotionAnalysis] = None
    voice_emotion: Optional[VoiceEmotionAnalysis] = None
    combined_emotion: Optional[str] = None
    combined_confidence: Optional[float] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class EmotionHistoryResponse(BaseModel):
    """Emotion analysis history for a user/session"""
    user_id: int
    session_id: Optional[str] = None
    emotions: list[EmotionAnalysisResponse]
    dominant_emotion: Optional[str] = None
    average_confidence: Optional[float] = None
