from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
from ..models.feedback import Feedback


class FeedbackRepository:
    """Repository for Feedback database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        chat_id: int,
        rating: int,
        feedback_type: str,
        comment: Optional[str] = None
    ) -> Feedback:
        """Create a new feedback entry"""
        feedback = Feedback(
            user_id=user_id,
            chat_id=chat_id,
            rating=rating,
            feedback_type=feedback_type,
            comment=comment,
            is_processed=False
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def get_by_id(self, feedback_id: int) -> Optional[Feedback]:
        """Get feedback by ID"""
        return self.db.query(Feedback).filter(Feedback.id == feedback_id).first()

    def get_user_feedbacks(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Feedback]:
        """Get all feedbacks from a specific user"""
        return (
            self.db.query(Feedback)
            .filter(Feedback.user_id == user_id)
            .order_by(desc(Feedback.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_chat_feedbacks(self, chat_id: int) -> List[Feedback]:
        """Get all feedbacks for a specific chat message"""
        return (
            self.db.query(Feedback)
            .filter(Feedback.chat_id == chat_id)
            .order_by(desc(Feedback.created_at))
            .all()
        )

    def get_unprocessed_feedbacks(self, limit: int = 100) -> List[Feedback]:
        """Get feedbacks that haven't been processed for bias analysis"""
        return (
            self.db.query(Feedback)
            .filter(Feedback.is_processed == False)
            .order_by(Feedback.created_at)
            .limit(limit)
            .all()
        )

    def mark_as_processed(self, feedback_ids: List[int]) -> int:
        """Mark feedbacks as processed"""
        count = (
            self.db.query(Feedback)
            .filter(Feedback.id.in_(feedback_ids))
            .update({Feedback.is_processed: True}, synchronize_session=False)
        )
        self.db.commit()
        return count

    def get_user_feedback_stats(self, user_id: int) -> Dict:
        """Get feedback statistics for a user"""
        feedbacks = self.get_user_feedbacks(user_id, limit=1000)

        if not feedbacks:
            return {
                "total": 0,
                "average_rating": 0.0,
                "by_type": {},
                "by_rating": {}
            }

        total = len(feedbacks)
        avg_rating = sum(f.rating for f in feedbacks) / total

        # Group by type
        by_type = {}
        for f in feedbacks:
            by_type[f.feedback_type] = by_type.get(f.feedback_type, 0) + 1

        # Group by rating
        by_rating = {}
        for f in feedbacks:
            by_rating[f.rating] = by_rating.get(f.rating, 0) + 1

        return {
            "total": total,
            "average_rating": round(avg_rating, 2),
            "by_type": by_type,
            "by_rating": by_rating
        }

    def get_negative_feedbacks(
        self,
        user_id: int,
        rating_threshold: int = 2,
        days: int = 30
    ) -> List[Feedback]:
        """Get negative feedbacks (low ratings) for bias analysis"""
        since_date = datetime.utcnow() - timedelta(days=days)

        return (
            self.db.query(Feedback)
            .filter(
                Feedback.user_id == user_id,
                Feedback.rating <= rating_threshold,
                Feedback.created_at >= since_date
            )
            .order_by(desc(Feedback.created_at))
            .all()
        )

    def get_feedbacks_by_type(
        self,
        user_id: int,
        feedback_type: str,
        days: int = 30
    ) -> List[Feedback]:
        """Get feedbacks by type for analysis"""
        since_date = datetime.utcnow() - timedelta(days=days)

        return (
            self.db.query(Feedback)
            .filter(
                Feedback.user_id == user_id,
                Feedback.feedback_type == feedback_type,
                Feedback.created_at >= since_date
            )
            .all()
        )

    def get_average_ratings_by_type(self, user_id: int) -> Dict[str, float]:
        """Get average ratings grouped by feedback type"""
        results = (
            self.db.query(
                Feedback.feedback_type,
                func.avg(Feedback.rating).label('avg_rating'),
                func.count(Feedback.id).label('count')
            )
            .filter(Feedback.user_id == user_id)
            .group_by(Feedback.feedback_type)
            .all()
        )

        return {
            row.feedback_type: {
                'average': round(row.avg_rating, 2),
                'count': row.count
            }
            for row in results
        }

    def get_recent_comments(
        self,
        user_id: int,
        days: int = 30,
        limit: int = 50
    ) -> List[Tuple[str, str, int]]:
        """Get recent feedback comments for text analysis"""
        since_date = datetime.utcnow() - timedelta(days=days)

        results = (
            self.db.query(
                Feedback.comment,
                Feedback.feedback_type,
                Feedback.rating
            )
            .filter(
                Feedback.user_id == user_id,
                Feedback.comment.isnot(None),
                Feedback.comment != '',
                Feedback.created_at >= since_date
            )
            .order_by(desc(Feedback.created_at))
            .limit(limit)
            .all()
        )

        return [(r.comment, r.feedback_type, r.rating) for r in results]

    def count_total_feedbacks(self, user_id: int) -> int:
        """Count total feedbacks for a user"""
        return self.db.query(Feedback).filter(Feedback.user_id == user_id).count()

    def delete_feedback(self, feedback_id: int, user_id: int) -> bool:
        """Delete a feedback (only if owned by user)"""
        result = (
            self.db.query(Feedback)
            .filter(Feedback.id == feedback_id, Feedback.user_id == user_id)
            .delete()
        )
        self.db.commit()
        return result > 0
