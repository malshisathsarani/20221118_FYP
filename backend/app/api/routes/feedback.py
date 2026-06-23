"""
Feedback API Routes

Endpoints for submitting and analyzing user feedback.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ..dependencies import get_current_user
from ...models.user import User
from ...schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackStats,
    FeedbackSummary
)
from ...services.feedback_service import FeedbackService
from ...ml.bias_reduction.bias_correction_algorithm import BiasReductionAlgorithm


router = APIRouter()


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit user feedback about bot responses or detections.

    This endpoint allows users to rate and comment on:
    - Emotion detection accuracy
    - Response quality
    - Crisis detection appropriateness
    - General bias reports

    The feedback is used to improve model performance and detect bias.
    """
    try:
        service = FeedbackService(db)
        feedback = service.submit_feedback(
            user_id=current_user.id,
            feedback_data=feedback_data
        )
        return feedback
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting feedback: {str(e)}"
        )


@router.get("/my-feedback", response_model=List[FeedbackResponse])
async def get_my_feedback(
    limit: int = 50,
    feedback_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all feedback submitted by the current user.

    Query Parameters:
    - limit: Maximum number of results (default 50)
    - feedback_type: Filter by type (optional)
    """
    try:
        service = FeedbackService(db)
        feedback_list = service.get_user_feedback(
            user_id=current_user.id,
            limit=limit,
            feedback_type=feedback_type
        )
        return feedback_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving feedback: {str(e)}"
        )


@router.get("/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    feedback_type: Optional[str] = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregated feedback statistics (Admin/Analytics).

    Query Parameters:
    - feedback_type: Filter by type (optional)
    - days: Number of days to analyze (default 30)

    Note: This could be restricted to admin users in production.
    """
    try:
        service = FeedbackService(db)
        stats = service.get_feedback_stats(
            feedback_type=feedback_type,
            days=days
        )
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving stats: {str(e)}"
        )


@router.get("/low-ratings", response_model=List[FeedbackResponse])
async def get_low_rating_feedback(
    threshold: int = 2,
    feedback_type: Optional[str] = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get feedback with low ratings (potential issues).

    Query Parameters:
    - threshold: Ratings <= this value (default 2)
    - feedback_type: Filter by type (optional)
    - days: Number of days to analyze (default 30)

    Useful for identifying problem areas in the system.
    """
    try:
        service = FeedbackService(db)
        feedback_list = service.get_low_rating_feedback(
            threshold=threshold,
            feedback_type=feedback_type,
            days=days
        )
        return feedback_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving low-rating feedback: {str(e)}"
        )


@router.get("/analysis/emotion-accuracy")
async def analyze_emotion_accuracy(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze emotion detection accuracy based on user feedback.

    Query Parameters:
    - days: Number of days to analyze (default 30)

    Returns analysis of emotion detection performance.
    """
    try:
        service = FeedbackService(db)
        analysis = service.analyze_emotion_accuracy(days=days)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing emotion accuracy: {str(e)}"
        )


@router.get("/analysis/crisis-detection")
async def analyze_crisis_detection(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze crisis detection accuracy based on user feedback.

    Query Parameters:
    - days: Number of days to analyze (default 30)

    Returns analysis of crisis detection performance.
    """
    try:
        service = FeedbackService(db)
        analysis = service.analyze_crisis_detection(days=days)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing crisis detection: {str(e)}"
        )


@router.get("/bias-report")
async def get_bias_report(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive bias analysis report.

    Query Parameters:
    - days: Number of days to analyze (default 30)

    Returns patterns, recommendations, and overall model health.
    """
    try:
        service = FeedbackService(db)
        report = service.generate_bias_report(days=days)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating bias report: {str(e)}"
        )


@router.get("/bias-correction-status")
async def get_bias_correction_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current status of bias correction algorithm.

    Shows:
    - Number of correction patterns learned
    - Confidence adjustments per emotion
    - Last refresh time
    - Top correction patterns

    This endpoint helps monitor the bias reduction system.
    """
    try:
        algorithm = BiasReductionAlgorithm(db)
        stats = algorithm.get_stats()
        return {
            "status": "active",
            "statistics": stats,
            "message": "Bias correction algorithm is learning from user feedback"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving bias correction status: {str(e)}"
        )


@router.post("/refresh-bias-algorithm")
async def refresh_bias_algorithm(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger refresh of bias correction algorithm.

    Useful for immediately incorporating new feedback
    without waiting for automatic hourly refresh.
    """
    try:
        algorithm = BiasReductionAlgorithm(db)
        algorithm.refresh()
        stats = algorithm.get_stats()

        return {
            "status": "success",
            "message": "Bias correction algorithm refreshed successfully",
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing bias algorithm: {str(e)}"
        )
