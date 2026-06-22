from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class FeedbackType(str, Enum):
    """Types of feedback a user can provide"""
    EMOTION_ACCURACY = "emotion_accuracy"
    RESPONSE_QUALITY = "response_quality"
    CRISIS_DETECTION = "crisis_detection"


class FeedbackCreate(BaseModel):
    """Schema for creating new feedback"""
    chat_id: int = Field(..., description="ID of the chat message being reviewed")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 (unhelpful) to 5 (helpful)")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    comment: Optional[str] = Field(None, max_length=500, description="Optional user comment")

    @validator('comment')
    def clean_comment(cls, v):
        """Clean and trim comment"""
        if v:
            return v.strip()
        return v


class FeedbackResponse(BaseModel):
    """Schema for feedback response"""
    id: int
    user_id: int
    chat_id: int
    rating: int
    feedback_type: str
    comment: Optional[str]
    is_processed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BiasPattern(BaseModel):
    """Detected bias pattern"""
    pattern_type: str = Field(..., description="Type of bias detected")
    occurrence_count: int = Field(..., description="Number of times this pattern occurred")
    severity: str = Field(..., description="Severity level: low, medium, high")
    example_comments: List[str] = Field(default_factory=list, description="Sample user comments")
    recommendation: str = Field(..., description="Suggested action to address this bias")


class BiasAnalysisResult(BaseModel):
    """Result of bias pattern analysis"""
    total_feedbacks: int = Field(..., description="Total number of feedbacks analyzed")
    negative_count: int = Field(..., description="Number of negative feedbacks (rating <= 2)")
    negative_percentage: float = Field(..., description="Percentage of negative feedback")

    # Breakdown by feedback type
    emotion_accuracy_score: float = Field(..., description="Avg rating for emotion accuracy")
    response_quality_score: float = Field(..., description="Avg rating for response quality")
    crisis_detection_score: float = Field(..., description="Avg rating for crisis detection")

    # Detected patterns
    bias_patterns: List[BiasPattern] = Field(default_factory=list, description="Detected bias patterns")

    # Overall recommendations
    recommendations: List[str] = Field(default_factory=list, description="Recommended improvements")

    # Analysis metadata
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    needs_model_review: bool = Field(False, description="Whether ML models need review")


class FeedbackStats(BaseModel):
    """Aggregated feedback statistics"""
    total_feedbacks: int
    average_rating: float
    ratings_distribution: Dict[int, int]  # {1: count, 2: count, ...}
    feedback_by_type: Dict[str, int]  # {emotion_accuracy: count, ...}
    recent_feedbacks: List[FeedbackResponse]

    class Config:
        from_attributes = True
