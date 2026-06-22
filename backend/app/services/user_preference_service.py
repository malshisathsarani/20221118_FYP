"""
User Preference Learning Service

This service tracks user feedback patterns and adjusts responses
in real-time WITHOUT retraining the model.

Key Features:
1. Learn user-specific emotion patterns from feedback
2. Adjust emotion detection for individual users
3. Track response preferences
4. Apply corrections in future conversations
"""

from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from collections import Counter

from ..models.feedback import Feedback
from ..models.chat import Chat


class UserPreferenceService:
    """Service for learning and applying user-specific preferences"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_emotion_corrections(self, user_id: int, days: int = 90) -> Dict[str, str]:
        """
        Learn user's emotion correction patterns from feedback.

        Returns mapping: detected_emotion -> actual_emotion

        Example:
        {
            "anger": "stress",  # User says anger detection is wrong, it's stress
            "sad": "tired"      # User says sad detection is wrong, it's tired
        }
        """
        # Get emotion accuracy feedback with comments
        feedbacks = (
            self.db.query(Feedback, Chat)
            .join(Chat, Feedback.chat_id == Chat.id)
            .filter(
                Feedback.user_id == user_id,
                Feedback.feedback_type == 'emotion_accuracy',
                Feedback.rating <= 2,  # Negative feedback
                Feedback.comment.isnot(None),
                Chat.detected_emotion.isnot(None),  # Changed from emotion_analysis
                Feedback.created_at >= datetime.utcnow() - timedelta(days=days)
            )
            .all()
        )

        corrections = {}

        for feedback, chat in feedbacks:
            detected_emotion = chat.detected_emotion  # Changed: direct attribute access
            comment = feedback.comment.lower()

            if not detected_emotion:
                continue

            # Parse user's correction from comment
            actual_emotion = self._extract_actual_emotion(comment)

            if actual_emotion and actual_emotion != detected_emotion:
                # Track this correction
                corrections[detected_emotion] = actual_emotion

        return corrections

    def _extract_actual_emotion(self, comment: str) -> Optional[str]:
        """
        Extract actual emotion from user's feedback comment.

        Examples:
        - "I'm stressed not angry" -> "stress"
        - "Wrong! I'm tired" -> "tired"
        - "Not sad, just anxious" -> "anxious"
        """
        emotion_keywords = {
            'stress': ['stressed', 'stress'],
            'anxious': ['anxious', 'anxiety', 'worried'],
            'sad': ['sad', 'sadness', 'depressed'],
            'happy': ['happy', 'joy', 'excited'],
            'angry': ['angry', 'anger', 'mad', 'frustrated'],
            'tired': ['tired', 'exhausted', 'fatigue'],
            'neutral': ['neutral', 'okay', 'fine'],
            'fear': ['scared', 'afraid', 'fear']
        }

        # Look for phrases like "I'm [emotion]" or "actually [emotion]"
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in comment:
                    return emotion

        return None

    def adjust_emotion_for_user(
        self,
        user_id: int,
        detected_emotion: str,
        confidence: float
    ) -> tuple[str, float, bool]:
        """
        Adjust emotion detection based on user's past feedback.

        Args:
            user_id: User ID
            detected_emotion: Emotion detected by ML model
            confidence: Model's confidence score

        Returns:
            (adjusted_emotion, adjusted_confidence, was_corrected)
        """
        corrections = self.get_user_emotion_corrections(user_id)

        if detected_emotion in corrections:
            # User has consistently corrected this emotion
            actual_emotion = corrections[detected_emotion]

            return (
                actual_emotion,
                confidence * 0.9,  # Slightly lower confidence for corrected emotion
                True  # Indicates this was corrected based on feedback
            )

        return (detected_emotion, confidence, False)

    def get_user_response_preferences(self, user_id: int) -> Dict[str, any]:
        """
        Learn user's response style preferences from feedback.

        Returns preferences like:
        - Preferred response length
        - Likes/dislikes generic responses
        - Prefers empathy vs. advice
        """
        feedbacks = (
            self.db.query(Feedback)
            .filter(
                Feedback.user_id == user_id,
                Feedback.feedback_type == 'response_quality',
                Feedback.comment.isnot(None)
            )
            .all()
        )

        preferences = {
            'avoid_generic': False,
            'prefer_personalized': False,
            'prefer_short_responses': False,
            'prefer_actionable_advice': False
        }

        # Analyze comments for patterns
        negative_comments = [f.comment.lower() for f in feedbacks if f.rating <= 2]

        for comment in negative_comments:
            if any(word in comment for word in ['generic', 'robotic', 'template']):
                preferences['avoid_generic'] = True
                preferences['prefer_personalized'] = True

            if any(word in comment for word in ['too long', 'verbose', 'short']):
                preferences['prefer_short_responses'] = True

            if any(word in comment for word in ['advice', 'action', 'what to do']):
                preferences['prefer_actionable_advice'] = True

        return preferences

    def should_skip_crisis_alert(self, user_id: int, crisis_score: float) -> bool:
        """
        Check if user has reported false positive crisis detections.

        Returns True if system should be more conservative for this user.
        """
        # Get crisis detection feedback
        feedbacks = (
            self.db.query(Feedback)
            .filter(
                Feedback.user_id == user_id,
                Feedback.feedback_type == 'crisis_detection',
                Feedback.rating <= 2  # Negative = false positive
            )
            .all()
        )

        if len(feedbacks) >= 3:
            # User has reported 3+ false positives
            # Be more conservative - only alert on very high scores
            return crisis_score < 0.85

        return False

    def get_user_feedback_summary(self, user_id: int) -> Dict:
        """
        Get summary of learned preferences for this user.

        Used to adjust bot behavior without retraining models.
        """
        emotion_corrections = self.get_user_emotion_corrections(user_id)
        response_prefs = self.get_user_response_preferences(user_id)

        # Get overall satisfaction
        recent_feedbacks = (
            self.db.query(Feedback)
            .filter(Feedback.user_id == user_id)
            .order_by(desc(Feedback.created_at))
            .limit(20)
            .all()
        )

        avg_rating = sum(f.rating for f in recent_feedbacks) / len(recent_feedbacks) if recent_feedbacks else 0

        return {
            "user_id": user_id,
            "learned_preferences": {
                "emotion_corrections": emotion_corrections,
                "response_preferences": response_prefs,
                "satisfaction_score": round(avg_rating, 2)
            },
            "total_feedbacks": len(recent_feedbacks),
            "learning_active": len(emotion_corrections) > 0 or any(response_prefs.values())
        }
