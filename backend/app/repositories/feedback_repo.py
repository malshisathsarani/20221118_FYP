"""
Feedback Repository - Data Access Layer

This repository handles all database operations for user feedback.
It supports bias detection by storing user corrections and ratings for ML predictions.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.feedback import Feedback
from ..models.chat import Chat


class FeedbackRepository:
    """
    Repository for managing user feedback data.

    Purpose:
    - Store user feedback about ML model predictions
    - Track emotion accuracy ratings
    - Collect crisis detection feedback
    - Enable bias detection through aggregated feedback analysis
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        chat_id: Optional[int],
        rating: int,
        feedback_type: str,
        comment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Feedback:
        """
        Create a new feedback entry.

        Args:
            user_id: ID of the user providing feedback
            chat_id: ID of the chat message being rated (optional)
            rating: 1-5 star rating (1=very poor, 5=excellent)
            feedback_type: Type of feedback
                - 'emotion_accuracy': Was the emotion detection correct?
                - 'response_quality': Was the chatbot response helpful?
                - 'crisis_detection': Was crisis detection appropriate?
                - 'bias_report': User reporting potential bias
            comment: Optional text explanation from user
            metadata: Additional structured data (e.g., expected_emotion, detected_emotion)

        Returns:
            Created Feedback object
        """
        feedback = Feedback(
            user_id=user_id,
            chat_id=chat_id,
            rating=rating,
            feedback_type=feedback_type,
            comment=comment,
            is_processed=False,
            created_at=datetime.utcnow()
        )

        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def get_by_id(self, feedback_id: int) -> Optional[Feedback]:
        """Get a specific feedback entry by ID."""
        return self.db.query(Feedback).filter(Feedback.id == feedback_id).first()

    def get_by_chat_id(self, chat_id: int) -> List[Feedback]:
        """Get all feedback for a specific chat message."""
        return self.db.query(Feedback).filter(Feedback.chat_id == chat_id).all()

    def get_user_feedback(
        self,
        user_id: int,
        limit: int = 50,
        feedback_type: Optional[str] = None
    ) -> List[Feedback]:
        """
        Get feedback submitted by a specific user.

        Args:
            user_id: User ID
            limit: Maximum number of results
            feedback_type: Optional filter by type
        """
        query = self.db.query(Feedback).filter(Feedback.user_id == user_id)

        if feedback_type:
            query = query.filter(Feedback.feedback_type == feedback_type)

        return query.order_by(desc(Feedback.created_at)).limit(limit).all()

    def get_unprocessed_feedback(
        self,
        feedback_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Feedback]:
        """
        Get feedback that hasn't been processed yet.

        Used by bias detection service to identify new feedback
        that needs analysis for model improvement.
        """
        query = self.db.query(Feedback).filter(Feedback.is_processed == False)

        if feedback_type:
            query = query.filter(Feedback.feedback_type == feedback_type)

        return query.order_by(Feedback.created_at).limit(limit).all()

    def mark_as_processed(self, feedback_id: int) -> bool:
        """Mark feedback as processed after bias analysis."""
        feedback = self.get_by_id(feedback_id)
        if feedback:
            feedback.is_processed = True
            self.db.commit()
            return True
        return False

    def mark_batch_as_processed(self, feedback_ids: List[int]) -> int:
        """Mark multiple feedback entries as processed. Returns count updated."""
        count = self.db.query(Feedback).filter(
            Feedback.id.in_(feedback_ids)
        ).update(
            {'is_processed': True},
            synchronize_session=False
        )
        self.db.commit()
        return count

    def get_low_rating_feedback(
        self,
        threshold: int = 2,
        feedback_type: Optional[str] = None,
        days: int = 30
    ) -> List[Feedback]:
        """
        Get feedback with low ratings (potential bias indicators).

        Low ratings suggest model predictions may be biased or inaccurate.

        Args:
            threshold: Ratings <= this value (default 2 = poor)
            feedback_type: Optional filter
            days: Look back this many days
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = self.db.query(Feedback).filter(
            and_(
                Feedback.rating <= threshold,
                Feedback.created_at >= cutoff_date
            )
        )

        if feedback_type:
            query = query.filter(Feedback.feedback_type == feedback_type)

        return query.order_by(desc(Feedback.created_at)).all()

    def get_feedback_stats(
        self,
        feedback_type: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get aggregated feedback statistics for bias analysis.

        Returns:
            Dict with average ratings, distribution, counts, etc.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = self.db.query(Feedback).filter(Feedback.created_at >= cutoff_date)

        if feedback_type:
            query = query.filter(Feedback.feedback_type == feedback_type)

        # Total count
        total_count = query.count()

        if total_count == 0:
            return {
                'total_count': 0,
                'average_rating': 0,
                'rating_distribution': {},
                'feedback_by_type': {},
                'low_rating_count': 0,
                'high_rating_count': 0
            }

        # Average rating
        avg_rating = query.with_entities(func.avg(Feedback.rating)).scalar() or 0

        # Rating distribution (1-5)
        rating_dist = {}
        for rating in range(1, 6):
            count = query.filter(Feedback.rating == rating).count()
            rating_dist[rating] = count

        # Feedback by type
        type_counts = self.db.query(
            Feedback.feedback_type,
            func.count(Feedback.id)
        ).filter(
            Feedback.created_at >= cutoff_date
        ).group_by(
            Feedback.feedback_type
        ).all()

        feedback_by_type = {ftype: count for ftype, count in type_counts}

        # Low vs high ratings
        low_count = query.filter(Feedback.rating <= 2).count()
        high_count = query.filter(Feedback.rating >= 4).count()

        return {
            'total_count': total_count,
            'average_rating': float(avg_rating),
            'rating_distribution': rating_dist,
            'feedback_by_type': feedback_by_type,
            'low_rating_count': low_count,
            'low_rating_percentage': (low_count / total_count * 100) if total_count > 0 else 0,
            'high_rating_count': high_count,
            'high_rating_percentage': (high_count / total_count * 100) if total_count > 0 else 0,
            'days': days
        }

    def get_emotion_accuracy_feedback(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get feedback specifically about emotion detection accuracy.

        Used to identify patterns where emotion detection is frequently wrong,
        which indicates bias or model limitations.

        Returns list of dicts with chat details and feedback.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Join with Chat to get actual predictions vs feedback
        results = self.db.query(
            Feedback,
            Chat.message,
            Chat.detected_emotion,
            Chat.emotion_confidence,
            Chat.audio_emotion
        ).join(
            Chat, Feedback.chat_id == Chat.id
        ).filter(
            and_(
                Feedback.feedback_type == 'emotion_accuracy',
                Feedback.created_at >= cutoff_date
            )
        ).all()

        feedback_data = []
        for feedback, message, detected_emotion, emotion_conf, audio_emotion in results:
            feedback_data.append({
                'feedback_id': feedback.id,
                'rating': feedback.rating,
                'comment': feedback.comment,
                'user_message': message,
                'detected_emotion': detected_emotion,
                'emotion_confidence': emotion_conf,
                'audio_emotion': audio_emotion,
                'created_at': feedback.created_at
            })

        return feedback_data

    def get_crisis_detection_feedback(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get feedback about crisis detection accuracy.

        Critical for identifying:
        - False positives (crisis detected when not present)
        - False negatives (crisis missed)
        - Cultural/contextual biases in crisis detection
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        results = self.db.query(
            Feedback,
            Chat.message,
            Chat.crisis_score,
            Chat.is_crisis,
            Chat.detected_emotion
        ).join(
            Chat, Feedback.chat_id == Chat.id
        ).filter(
            and_(
                Feedback.feedback_type == 'crisis_detection',
                Feedback.created_at >= cutoff_date
            )
        ).all()

        feedback_data = []
        for feedback, message, crisis_score, is_crisis, emotion in results:
            feedback_data.append({
                'feedback_id': feedback.id,
                'rating': feedback.rating,
                'comment': feedback.comment,
                'user_message': message,
                'crisis_score': crisis_score,
                'is_crisis': is_crisis,
                'detected_emotion': emotion,
                'created_at': feedback.created_at
            })

        return feedback_data

    def delete(self, feedback_id: int) -> bool:
        """Delete a feedback entry."""
        feedback = self.get_by_id(feedback_id)
        if feedback:
            self.db.delete(feedback)
            self.db.commit()
            return True
        return False
