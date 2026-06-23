"""
Feedback Service - Business Logic Layer

This service handles feedback submission and analysis for bias detection.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ..repositories.feedback_repo import FeedbackRepository
from ..schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackStats,
    BiasAnalysisReport,
    BiasPattern
)
from datetime import datetime


class FeedbackService:
    """
    Service for managing user feedback and bias detection.

    This service:
    - Processes user feedback submissions
    - Aggregates feedback for bias analysis
    - Generates reports on model performance
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = FeedbackRepository(db)

    def submit_feedback(
        self,
        user_id: int,
        feedback_data: FeedbackCreate
    ) -> FeedbackResponse:
        """
        Submit user feedback.

        Args:
            user_id: ID of the user providing feedback
            feedback_data: Feedback details (rating, type, comment, etc.)

        Returns:
            Created feedback response
        """
        feedback = self.repo.create(
            user_id=user_id,
            chat_id=feedback_data.chat_id,
            rating=feedback_data.rating,
            feedback_type=feedback_data.feedback_type.value,
            comment=feedback_data.comment,
            metadata=feedback_data.metadata
        )

        return FeedbackResponse.model_validate(feedback)

    def get_user_feedback(
        self,
        user_id: int,
        limit: int = 50,
        feedback_type: Optional[str] = None
    ) -> List[FeedbackResponse]:
        """
        Get all feedback submitted by a user.

        Args:
            user_id: User ID
            limit: Maximum number of results
            feedback_type: Optional filter by type

        Returns:
            List of feedback responses
        """
        feedback_list = self.repo.get_user_feedback(
            user_id=user_id,
            limit=limit,
            feedback_type=feedback_type
        )

        return [FeedbackResponse.model_validate(f) for f in feedback_list]

    def get_feedback_stats(
        self,
        feedback_type: Optional[str] = None,
        days: int = 30
    ) -> FeedbackStats:
        """
        Get aggregated feedback statistics.

        Args:
            feedback_type: Optional filter by type
            days: Number of days to analyze

        Returns:
            Aggregated statistics
        """
        stats_dict = self.repo.get_feedback_stats(
            feedback_type=feedback_type,
            days=days
        )

        return FeedbackStats(**stats_dict)

    def get_low_rating_feedback(
        self,
        threshold: int = 2,
        feedback_type: Optional[str] = None,
        days: int = 30
    ) -> List[FeedbackResponse]:
        """
        Get feedback with low ratings (potential issues).

        Args:
            threshold: Ratings <= this value
            feedback_type: Optional filter
            days: Days to look back

        Returns:
            List of low-rated feedback
        """
        feedback_list = self.repo.get_low_rating_feedback(
            threshold=threshold,
            feedback_type=feedback_type,
            days=days
        )

        return [FeedbackResponse.model_validate(f) for f in feedback_list]

    def analyze_emotion_accuracy(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze emotion detection accuracy based on user feedback.

        Returns:
            Analysis of emotion detection performance
        """
        feedback_data = self.repo.get_emotion_accuracy_feedback(days=days)

        if not feedback_data:
            return {
                'total_feedback': 0,
                'average_rating': 0,
                'common_issues': [],
                'needs_improvement': False
            }

        total = len(feedback_data)
        avg_rating = sum(f['rating'] for f in feedback_data) / total
        low_ratings = [f for f in feedback_data if f['rating'] <= 2]

        # Extract common issues from comments
        common_issues = []
        for f in low_ratings:
            if f['comment']:
                common_issues.append({
                    'comment': f['comment'],
                    'detected_emotion': f['detected_emotion'],
                    'rating': f['rating']
                })

        return {
            'total_feedback': total,
            'average_rating': round(avg_rating, 2),
            'low_rating_count': len(low_ratings),
            'low_rating_percentage': round(len(low_ratings) / total * 100, 2),
            'common_issues': common_issues[:10],  # Top 10 issues
            'needs_improvement': avg_rating < 3.5 or len(low_ratings) / total > 0.2
        }

    def analyze_crisis_detection(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze crisis detection accuracy based on user feedback.

        Returns:
            Analysis of crisis detection performance
        """
        feedback_data = self.repo.get_crisis_detection_feedback(days=days)

        if not feedback_data:
            return {
                'total_feedback': 0,
                'average_rating': 0,
                'false_positives': 0,
                'false_negatives': 0,
                'needs_adjustment': False
            }

        total = len(feedback_data)
        avg_rating = sum(f['rating'] for f in feedback_data) / total
        low_ratings = [f for f in feedback_data if f['rating'] <= 2]

        # Identify potential false positives (crisis detected but low rating)
        false_positives = [f for f in low_ratings if f['is_crisis'] == 1]

        return {
            'total_feedback': total,
            'average_rating': round(avg_rating, 2),
            'low_rating_count': len(low_ratings),
            'potential_false_positives': len(false_positives),
            'false_positive_percentage': round(len(false_positives) / total * 100, 2) if total > 0 else 0,
            'needs_adjustment': avg_rating < 3.5 or len(false_positives) / total > 0.15
        }

    def generate_bias_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate a comprehensive bias analysis report.

        Args:
            days: Number of days to analyze

        Returns:
            Bias analysis report with patterns and recommendations
        """
        # Get overall stats
        overall_stats = self.repo.get_feedback_stats(days=days)

        # Get emotion accuracy analysis
        emotion_analysis = self.analyze_emotion_accuracy(days=days)

        # Get crisis detection analysis
        crisis_analysis = self.analyze_crisis_detection(days=days)

        # Identify bias patterns
        bias_patterns = []

        if emotion_analysis.get('needs_improvement'):
            bias_patterns.append({
                'pattern_type': 'emotion_misclassification',
                'description': 'Emotion detection accuracy is below acceptable threshold',
                'severity': 'high' if emotion_analysis['average_rating'] < 3.0 else 'medium',
                'affected_count': emotion_analysis['low_rating_count'],
                'recommended_action': 'Review and retrain emotion detection model'
            })

        if crisis_analysis.get('needs_adjustment'):
            bias_patterns.append({
                'pattern_type': 'crisis_detection_issues',
                'description': 'Crisis detection has high false positive rate',
                'severity': 'high' if crisis_analysis.get('false_positive_percentage', 0) > 20 else 'medium',
                'affected_count': crisis_analysis.get('potential_false_positives', 0),
                'recommended_action': 'Adjust crisis detection threshold or retrain model'
            })

        # Determine overall health
        avg_rating = overall_stats.get('average_rating', 0)
        if avg_rating >= 4.0:
            health = 'excellent'
        elif avg_rating >= 3.5:
            health = 'good'
        elif avg_rating >= 3.0:
            health = 'fair'
        else:
            health = 'poor'

        return {
            'report_date': datetime.utcnow().isoformat(),
            'total_feedback_analyzed': overall_stats.get('total_count', 0),
            'bias_patterns': bias_patterns,
            'overall_model_health': health,
            'emotion_analysis': emotion_analysis,
            'crisis_analysis': crisis_analysis,
            'needs_retraining': len(bias_patterns) > 0,
            'retraining_priority': 'high' if health in ['poor', 'fair'] else 'low'
        }
