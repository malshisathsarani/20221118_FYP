"""
Feedback Schemas - Request/Response Data Models

These Pydantic models define the structure of feedback data
for API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class FeedbackType(str, Enum):
    """
    Types of feedback users can provide.

    Each type helps identify different sources of bias:
    - EMOTION_ACCURACY: Was the emotion correctly detected?
    - RESPONSE_QUALITY: Was the bot's response appropriate?
    - CRISIS_DETECTION: Was crisis detection appropriate (false positive/negative)?
    - BIAS_REPORT: User explicitly reporting perceived bias
    """
    EMOTION_ACCURACY = "emotion_accuracy"
    RESPONSE_QUALITY = "response_quality"
    CRISIS_DETECTION = "crisis_detection"
    BIAS_REPORT = "bias_report"


class FeedbackCreate(BaseModel):
    """
    Request model for creating feedback.

    Example usage in Flutter:
    ```dart
    {
      "chat_id": 123,
      "rating": 2,
      "feedback_type": "emotion_accuracy",
      "comment": "I wasn't angry, I was just surprised",
      "metadata": {
        "expected_emotion": "surprise",
        "detected_emotion": "anger"
      }
    }
    ```
    """
    chat_id: Optional[int] = Field(None, description="Chat message being rated (optional)")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 (very poor) to 5 (excellent)")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional explanation")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional structured data")

    @validator('rating')
    def validate_rating(cls, v):
        """Ensure rating is between 1-5."""
        if not 1 <= v <= 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

    class Config:
        schema_extra = {
            "example": {
                "chat_id": 123,
                "rating": 2,
                "feedback_type": "emotion_accuracy",
                "comment": "The emotion detected was incorrect. I wasn't sad, just tired.",
                "metadata": {
                    "expected_emotion": "neutral",
                    "detected_emotion": "sadness"
                }
            }
        }


class FeedbackResponse(BaseModel):
    """
    Response model for feedback data.
    """
    id: int
    user_id: int
    chat_id: Optional[int]
    rating: int
    feedback_type: str
    comment: Optional[str]
    is_processed: bool
    created_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class FeedbackStats(BaseModel):
    """
    Aggregated feedback statistics.

    Used to identify bias patterns:
    - Low average rating → model performing poorly
    - High low_rating_percentage → consistent issues
    - Specific feedback_by_type issues → targeted bias
    """
    total_count: int = Field(..., description="Total feedback entries")
    average_rating: float = Field(..., description="Average rating (1-5)")
    rating_distribution: Dict[int, int] = Field(..., description="Count per rating (1-5)")
    feedback_by_type: Dict[str, int] = Field(..., description="Count per feedback type")
    low_rating_count: int = Field(..., description="Number of ratings <= 2")
    low_rating_percentage: float = Field(..., description="Percentage of low ratings")
    high_rating_count: int = Field(..., description="Number of ratings >= 4")
    high_rating_percentage: float = Field(..., description="Percentage of high ratings")
    days: int = Field(..., description="Days included in analysis")

    class Config:
        schema_extra = {
            "example": {
                "total_count": 150,
                "average_rating": 3.8,
                "rating_distribution": {1: 5, 2: 10, 3: 30, 4: 60, 5: 45},
                "feedback_by_type": {
                    "emotion_accuracy": 80,
                    "response_quality": 50,
                    "crisis_detection": 20
                },
                "low_rating_count": 15,
                "low_rating_percentage": 10.0,
                "high_rating_count": 105,
                "high_rating_percentage": 70.0,
                "days": 30
            }
        }


class BiasPattern(BaseModel):
    """
    Identified bias pattern from feedback analysis.

    Example:
    - Emotion detection consistently wrong for certain emotions
    - Crisis detection has high false positive rate
    - Response quality low for specific topics
    """
    pattern_type: str = Field(..., description="Type of bias detected")
    description: str = Field(..., description="Human-readable description")
    severity: str = Field(..., description="low, medium, high, critical")
    affected_count: int = Field(..., description="Number of instances")
    examples: List[str] = Field(..., description="Sample feedback comments")
    recommended_action: str = Field(..., description="Suggested fix")

    class Config:
        schema_extra = {
            "example": {
                "pattern_type": "emotion_misclassification",
                "description": "Anger frequently misclassified as sadness",
                "severity": "high",
                "affected_count": 23,
                "examples": [
                    "I was angry, not sad!",
                    "Detected sadness but I was frustrated",
                    "This is anger, not sadness"
                ],
                "recommended_action": "Retrain emotion model with more anger examples"
            }
        }


class BiasAnalysisReport(BaseModel):
    """
    Comprehensive bias analysis report.

    Generated from aggregated feedback to identify
    systematic issues requiring model improvement.
    """
    report_date: datetime
    total_feedback_analyzed: int
    bias_patterns: List[BiasPattern]
    overall_model_health: str = Field(..., description="excellent, good, fair, poor")
    recommendations: List[str]
    needs_retraining: bool
    retraining_priority: str = Field(..., description="low, medium, high, critical")

    class Config:
        schema_extra = {
            "example": {
                "report_date": "2024-01-15T10:00:00",
                "total_feedback_analyzed": 150,
                "bias_patterns": [
                    {
                        "pattern_type": "emotion_misclassification",
                        "description": "Anger frequently misclassified as sadness",
                        "severity": "high",
                        "affected_count": 23,
                        "examples": ["I was angry, not sad!"],
                        "recommended_action": "Retrain emotion model with more anger examples"
                    }
                ],
                "overall_model_health": "good",
                "recommendations": [
                    "Collect more training data for anger emotion",
                    "Review crisis detection threshold"
                ],
                "needs_retraining": True,
                "retraining_priority": "medium"
            }
        }


class EmotionFeedbackDetail(BaseModel):
    """
    Detailed feedback about emotion detection.

    Used to create training data for model improvement.
    """
    feedback_id: int
    rating: int
    comment: Optional[str]
    user_message: str
    detected_emotion: str
    emotion_confidence: Optional[float]
    audio_emotion: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CrisisFeedbackDetail(BaseModel):
    """
    Detailed feedback about crisis detection.

    Critical for identifying false positives/negatives.
    """
    feedback_id: int
    rating: int
    comment: Optional[str]
    user_message: str
    crisis_score: float
    is_crisis: int
    detected_emotion: str
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackSummary(BaseModel):
    """
    Summary of user's feedback history.
    """
    user_id: int
    total_feedback_count: int
    average_rating: float
    recent_feedback: List[FeedbackResponse]

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "total_feedback_count": 25,
                "average_rating": 4.2,
                "recent_feedback": []
            }
        }
