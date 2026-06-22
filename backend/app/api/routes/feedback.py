from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    BiasAnalysisResult,
    FeedbackStats
)
from ...services.feedback_service import FeedbackService
from ..dependencies import get_current_user_id


router = APIRouter()


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    feedback: FeedbackCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Submit feedback on a chat response.

    This endpoint allows users to rate chat responses and provide comments,
    which are used for bias detection and model improvement.

    Endpoint: POST /api/feedback/

    Headers:
    - Authorization: Bearer <access_token>

    Request Body:
    - chat_id: ID of the chat message being reviewed
    - rating: 1-5 stars (1 = unhelpful, 5 = very helpful)
    - feedback_type: emotion_accuracy | response_quality | crisis_detection
    - comment: Optional text feedback (max 500 chars)

    Example:
    {
        "chat_id": 123,
        "rating": 4,
        "feedback_type": "response_quality",
        "comment": "Helpful but could be more personalized"
    }

    Returns:
    - Feedback confirmation with ID and timestamp
    """
    try:
        service = FeedbackService(db)
        result = service.submit_feedback(user_id, feedback)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/my-feedbacks", response_model=List[FeedbackResponse])
def get_my_feedbacks(
    limit: int = 50,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get current user's feedback history.

    Endpoint: GET /api/feedback/my-feedbacks?limit=50&offset=0

    Headers:
    - Authorization: Bearer <access_token>

    Query Parameters:
    - limit: Number of feedbacks to return (default: 50)
    - offset: Pagination offset (default: 0)

    Returns:
    - List of user's feedbacks ordered by most recent
    """
    try:
        service = FeedbackService(db)
        return service.get_user_feedbacks(user_id, limit, offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve feedbacks: {str(e)}"
        )


@router.get("/bias-analysis", response_model=BiasAnalysisResult)
def get_bias_analysis(
    days: int = 30,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get bias pattern analysis for current user's feedback.

    This is a key research feature that automatically detects bias patterns
    in the ML model responses based on user feedback.

    Endpoint: GET /api/feedback/bias-analysis?days=30

    Headers:
    - Authorization: Bearer <access_token>

    Query Parameters:
    - days: Analysis window in days (default: 30)

    Returns:
    - Comprehensive bias analysis including:
      - Total feedback count and negative percentage
      - Average scores by feedback type
      - Detected bias patterns with severity levels
      - Actionable recommendations for model improvement
      - Flag indicating if model review is needed

    Example Response:
    {
        "total_feedbacks": 45,
        "negative_count": 8,
        "negative_percentage": 17.78,
        "emotion_accuracy_score": 4.2,
        "response_quality_score": 3.8,
        "crisis_detection_score": 4.5,
        "bias_patterns": [
            {
                "pattern_type": "emotion",
                "occurrence_count": 3,
                "severity": "medium",
                "example_comments": ["Wrong emotion detected", ...],
                "recommendation": "Consider retraining emotion model..."
            }
        ],
        "recommendations": [
            "Response quality needs improvement (score: 3.8/5)..."
        ],
        "needs_model_review": false
    }

    Use Cases:
    - Research analysis of model bias
    - Identifying areas for improvement
    - Monitoring model performance over time
    - Generating reports for thesis/publication
    """
    try:
        service = FeedbackService(db)
        return service.analyze_bias_patterns(user_id, days)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze bias patterns: {str(e)}"
        )


@router.get("/stats", response_model=FeedbackStats)
def get_feedback_stats(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get aggregated feedback statistics.

    Endpoint: GET /api/feedback/stats

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - Overall feedback statistics including:
      - Total feedback count
      - Average rating
      - Distribution by rating (1-5 stars)
      - Distribution by feedback type
      - Recent feedbacks
    """
    try:
        service = FeedbackService(db)
        return service.get_feedback_stats(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}"
        )


@router.get("/export-training-data")
def export_training_data(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Export negative feedback for model retraining.

    This endpoint extracts chat messages that received negative feedback
    along with user corrections, formatted for ML model fine-tuning.

    Endpoint: GET /api/feedback/export-training-data

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - Training dataset with original messages, bot responses,
      actual emotions (from user feedback), and corrected responses

    Use Case:
    - After identifying bias patterns, export this data
    - Use it to fine-tune emotion detection or response generation models
    - Creates a supervised learning dataset from user corrections
    """
    try:
        service = FeedbackService(db)
        return service.export_training_data(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export training data: {str(e)}"
        )


@router.get("/user-preferences")
def get_user_preferences(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get user's learned preferences from feedback.

    This shows what the system has learned about this user's preferences
    through their feedback, including emotion corrections and response style.

    Endpoint: GET /api/feedback/user-preferences

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - Emotion corrections learned from feedback
    - Response style preferences
    - Overall satisfaction score
    - Whether learning is active for this user

    Example Response:
    {
        "user_id": 123,
        "learned_preferences": {
            "emotion_corrections": {
                "anger": "stress",
                "sad": "tired"
            },
            "response_preferences": {
                "avoid_generic": true,
                "prefer_personalized": true,
                "prefer_short_responses": false,
                "prefer_actionable_advice": true
            },
            "satisfaction_score": 3.8
        },
        "total_feedbacks": 15,
        "learning_active": true
    }

    Use Case:
    - Monitor personalization for individual users
    - Verify feedback learning is working
    - Debug why responses changed for a user
    - Research: demonstrate adaptive learning
    """
    try:
        from ...services.user_preference_service import UserPreferenceService
        pref_service = UserPreferenceService(db)
        return pref_service.get_user_feedback_summary(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user preferences: {str(e)}"
        )
