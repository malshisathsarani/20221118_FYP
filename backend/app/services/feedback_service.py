from typing import List, Dict, Optional
from datetime import datetime
import re
from collections import Counter
from sqlalchemy.orm import Session

from ..repositories.feedback_repo import FeedbackRepository
from ..schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    BiasAnalysisResult,
    BiasPattern,
    FeedbackStats
)
from ..models.feedback import Feedback


class FeedbackService:
    """Service for handling feedback and bias detection"""

    # Keywords that indicate potential bias issues
    BIAS_KEYWORDS = {
        'emotion': ['wrong emotion', 'incorrect emotion', 'misunderstood', 'not accurate',
                   'wrong feeling', 'doesn\'t understand'],
        'cultural': ['cultural', 'insensitive', 'offensive', 'inappropriate', 'disrespectful',
                    'doesn\'t understand my culture', 'not culturally'],
        'crisis': ['missed crisis', 'didn\'t detect', 'failed to recognize', 'ignored warning',
                  'should have detected', 'missed the signs'],
        'response': ['unhelpful', 'generic', 'robotic', 'doesn\'t help', 'not personalized',
                    'copy paste', 'template', 'repetitive']
    }

    def __init__(self, db: Session):
        self.db = db
        self.repo = FeedbackRepository(db)

    def submit_feedback(
        self,
        user_id: int,
        feedback_data: FeedbackCreate
    ) -> FeedbackResponse:
        """Submit new feedback"""

        # Create feedback in database
        feedback = self.repo.create(
            user_id=user_id,
            chat_id=feedback_data.chat_id,
            rating=feedback_data.rating,
            feedback_type=feedback_data.feedback_type.value,
            comment=feedback_data.comment
        )

        return FeedbackResponse.from_orm(feedback)

    def get_user_feedbacks(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[FeedbackResponse]:
        """Get user's feedback history"""
        feedbacks = self.repo.get_user_feedbacks(user_id, limit, offset)
        return [FeedbackResponse.from_orm(f) for f in feedbacks]

    def analyze_bias_patterns(
        self,
        user_id: int,
        days: int = 30
    ) -> BiasAnalysisResult:
        """
        Analyze feedback to detect bias patterns

        This is the core research contribution - automated bias detection
        that identifies problematic patterns in ML model responses.
        """

        # Get all feedbacks for analysis
        all_feedbacks = self.repo.get_user_feedbacks(user_id, limit=1000)

        if not all_feedbacks:
            return self._empty_analysis()

        # Filter to recent feedbacks
        negative_feedbacks = self.repo.get_negative_feedbacks(user_id, rating_threshold=2, days=days)

        # Calculate basic stats
        total = len(all_feedbacks)
        negative_count = len(negative_feedbacks)
        negative_percentage = (negative_count / total * 100) if total > 0 else 0.0

        # Get average ratings by type
        avg_by_type = self.repo.get_average_ratings_by_type(user_id)

        emotion_score = avg_by_type.get('emotion_accuracy', {}).get('average', 0.0)
        response_score = avg_by_type.get('response_quality', {}).get('average', 0.0)
        crisis_score = avg_by_type.get('crisis_detection', {}).get('average', 0.0)

        # Detect bias patterns
        bias_patterns = self._detect_bias_patterns(user_id, negative_feedbacks, days)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            emotion_score,
            response_score,
            crisis_score,
            negative_percentage,
            bias_patterns
        )

        # Determine if model needs review
        needs_review = (
            negative_percentage > 30 or
            emotion_score < 3.0 or
            crisis_score < 3.0 or
            len(bias_patterns) > 3
        )

        return BiasAnalysisResult(
            total_feedbacks=total,
            negative_count=negative_count,
            negative_percentage=round(negative_percentage, 2),
            emotion_accuracy_score=emotion_score,
            response_quality_score=response_score,
            crisis_detection_score=crisis_score,
            bias_patterns=bias_patterns,
            recommendations=recommendations,
            needs_model_review=needs_review
        )

    def _detect_bias_patterns(
        self,
        user_id: int,
        negative_feedbacks: List[Feedback],
        days: int
    ) -> List[BiasPattern]:
        """Detect specific bias patterns from negative feedback"""

        patterns = []

        # Get comments for text analysis
        comments = self.repo.get_recent_comments(user_id, days=days)

        if not comments:
            return patterns

        # Analyze comments for bias keywords
        for category, keywords in self.BIAS_KEYWORDS.items():
            matching_comments = []
            count = 0

            for comment_text, feedback_type, rating in comments:
                if rating <= 2:  # Only negative feedback
                    comment_lower = comment_text.lower()
                    if any(keyword in comment_lower for keyword in keywords):
                        matching_comments.append(comment_text)
                        count += 1

            if count > 0:
                # Determine severity based on occurrence
                if count >= 5:
                    severity = "high"
                elif count >= 3:
                    severity = "medium"
                else:
                    severity = "low"

                # Generate category-specific recommendations
                recommendation = self._get_pattern_recommendation(category, count)

                patterns.append(BiasPattern(
                    pattern_type=category,
                    occurrence_count=count,
                    severity=severity,
                    example_comments=matching_comments[:3],  # Include up to 3 examples
                    recommendation=recommendation
                ))

        # Check for repeated low ratings by type
        patterns.extend(self._detect_type_specific_issues(user_id, days))

        return patterns

    def _detect_type_specific_issues(self, user_id: int, days: int) -> List[BiasPattern]:
        """Detect issues specific to feedback types"""
        patterns = []

        for feedback_type in ['emotion_accuracy', 'response_quality', 'crisis_detection']:
            feedbacks = self.repo.get_feedbacks_by_type(user_id, feedback_type, days)

            if not feedbacks:
                continue

            # Calculate average rating
            avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
            low_count = sum(1 for f in feedbacks if f.rating <= 2)

            # If more than 40% are low ratings, flag as issue
            if len(feedbacks) >= 5 and low_count / len(feedbacks) > 0.4:
                severity = "high" if avg_rating < 2.0 else "medium"

                patterns.append(BiasPattern(
                    pattern_type=f"{feedback_type}_systematic_issue",
                    occurrence_count=low_count,
                    severity=severity,
                    example_comments=[],
                    recommendation=self._get_systematic_issue_recommendation(feedback_type, avg_rating)
                ))

        return patterns

    def _get_pattern_recommendation(self, category: str, count: int) -> str:
        """Generate recommendation based on detected pattern category"""
        recommendations = {
            'emotion': f"Emotion detection model showing {count} accuracy complaints. Consider retraining with more diverse emotional expression data.",
            'cultural': f"Cultural sensitivity issues detected in {count} responses. Review RAG knowledge base for cultural bias and expand with diverse cultural perspectives.",
            'crisis': f"Crisis detection missed {count} critical situations. Review crisis detection thresholds and training data for edge cases.",
            'response': f"Response quality issues in {count} cases. Enhance response personalization and review template diversity."
        }
        return recommendations.get(category, "Review and improve model performance in this area.")

    def _get_systematic_issue_recommendation(self, feedback_type: str, avg_rating: float) -> str:
        """Generate recommendation for systematic issues by type"""
        recommendations = {
            'emotion_accuracy': f"Emotion detection consistently rated {avg_rating:.1f}/5. Consider model fine-tuning on user-specific data or expanding emotion categories.",
            'response_quality': f"Response quality rated {avg_rating:.1f}/5. Improve RAG retrieval relevance and response personalization algorithms.",
            'crisis_detection': f"Crisis detection rated {avg_rating:.1f}/5. Critical issue - review detection sensitivity and false negative rate immediately."
        }
        return recommendations.get(feedback_type, f"Systematic issue detected with average rating {avg_rating:.1f}/5.")

    def _generate_recommendations(
        self,
        emotion_score: float,
        response_score: float,
        crisis_score: float,
        negative_percentage: float,
        bias_patterns: List[BiasPattern]
    ) -> List[str]:
        """Generate overall recommendations based on analysis"""
        recommendations = []

        # Overall negative feedback threshold
        if negative_percentage > 40:
            recommendations.append(
                f"⚠️ HIGH ALERT: {negative_percentage:.1f}% negative feedback. Immediate model review required."
            )
        elif negative_percentage > 25:
            recommendations.append(
                f"⚠️ Warning: {negative_percentage:.1f}% negative feedback. Consider model improvements."
            )

        # Emotion accuracy
        if emotion_score < 3.0:
            recommendations.append(
                f"🎭 Emotion detection needs improvement (score: {emotion_score:.1f}/5). Review emotion classification model."
            )

        # Crisis detection (most critical)
        if crisis_score < 3.5:
            recommendations.append(
                f"🚨 CRITICAL: Crisis detection rated {crisis_score:.1f}/5. This is life-critical - prioritize improvements immediately."
            )

        # Response quality
        if response_score < 3.0:
            recommendations.append(
                f"💬 Response quality needs improvement (score: {response_score:.1f}/5). Enhance RAG system and personalization."
            )

        # High-severity patterns
        high_severity_patterns = [p for p in bias_patterns if p.severity == "high"]
        if high_severity_patterns:
            recommendations.append(
                f"⚡ {len(high_severity_patterns)} high-severity bias patterns detected. See detailed patterns for specific actions."
            )

        # If everything is good
        if not recommendations:
            recommendations.append(
                "✅ No critical issues detected. Continue monitoring feedback for emerging patterns."
            )

        return recommendations

    def _empty_analysis(self) -> BiasAnalysisResult:
        """Return empty analysis when no feedback exists"""
        return BiasAnalysisResult(
            total_feedbacks=0,
            negative_count=0,
            negative_percentage=0.0,
            emotion_accuracy_score=0.0,
            response_quality_score=0.0,
            crisis_detection_score=0.0,
            bias_patterns=[],
            recommendations=["No feedback data available yet. Encourage users to provide feedback."],
            needs_model_review=False
        )

    def get_feedback_stats(self, user_id: int) -> FeedbackStats:
        """Get aggregated feedback statistics"""

        stats = self.repo.get_user_feedback_stats(user_id)
        recent = self.repo.get_user_feedbacks(user_id, limit=10)

        return FeedbackStats(
            total_feedbacks=stats['total'],
            average_rating=stats['average_rating'],
            ratings_distribution=stats['by_rating'],
            feedback_by_type=stats['by_type'],
            recent_feedbacks=[FeedbackResponse.from_orm(f) for f in recent]
        )

    def export_training_data(self, user_id: int) -> Dict:
        """
        Export feedback data for ML model retraining.

        Extracts negative feedback with chat context to create
        a supervised learning dataset for model fine-tuning.
        """
        from ..models.chat import Chat

        # Get negative feedbacks
        negative_feedbacks = self.repo.get_negative_feedbacks(user_id, rating_threshold=2, days=90)

        training_data = []

        for feedback in negative_feedbacks:
            # Get the original chat message
            chat = self.db.query(Chat).filter(Chat.id == feedback.chat_id).first()

            if not chat:
                continue

            # Extract emotion information if available
            detected_emotion = chat.detected_emotion

            # Build training example
            example = {
                "input": {
                    "user_message": chat.message,
                    "bot_response": chat.response,
                    "detected_emotion": detected_emotion,
                    "crisis_detected": bool(chat.is_crisis)
                },
                "feedback": {
                    "rating": feedback.rating,
                    "type": feedback.feedback_type,
                    "comment": feedback.comment,
                    "timestamp": feedback.created_at.isoformat()
                },
                "metadata": {
                    "chat_id": chat.id,
                    "feedback_id": feedback.id
                }
            }

            training_data.append(example)

        # Mark feedbacks as processed
        feedback_ids = [f.id for f in negative_feedbacks]
        if feedback_ids:
            self.repo.mark_as_processed(feedback_ids)

        return {
            "total_examples": len(training_data),
            "export_date": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "training_data": training_data,
            "usage_notes": {
                "purpose": "Fine-tune emotion detection and response generation models",
                "format": "Each example contains user message, bot response, detected values, and user feedback",
                "next_steps": [
                    "1. Review comments to identify correct emotions/responses",
                    "2. Create labeled dataset with corrections",
                    "3. Fine-tune models using this supervised data",
                    "4. Validate improvements with held-out test set"
                ]
            }
        }
