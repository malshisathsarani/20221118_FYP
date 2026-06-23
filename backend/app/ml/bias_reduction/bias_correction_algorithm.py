"""
Algorithmic Bias Reduction System

This module implements bias reduction through statistical algorithms
rather than model retraining. It learns from user feedback to:
1. Identify misclassification patterns
2. Adjust prediction confidence
3. Apply contextual corrections
4. Ensemble multiple signals
"""

from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class BiasReductionAlgorithm:
    """
    Algorithmic bias reduction without model retraining.
    Uses statistical patterns from user feedback to correct predictions.
    """

    def __init__(self, db: Session):
        self.db = db
        # Cache corrections in memory for fast access
        self.correction_patterns = {}
        self.confidence_adjustments = {}
        self.last_refresh = None

        # Initialize
        self.refresh()

    # ========== ALGORITHM 1: PATTERN-BASED CORRECTION ==========

    def build_correction_patterns(self) -> Dict[str, int]:
        """
        Algorithm: Build correction rules from feedback.

        Logic:
        - If emotion X is frequently rated low → penalize it
        - If users say "should be Y" when model says X → create rule X→Y

        Returns:
            {
                'anger→sadness': 23,  # anger misclassified as sadness 23 times
                'fear→anxiety': 12,
                ...
            }
        """
        from ...repositories.feedback_repo import FeedbackRepository
        from ...models.chat import Chat

        repo = FeedbackRepository(self.db)

        # Get low-rated emotion predictions (last 90 days)
        low_feedback = repo.get_low_rating_feedback(
            threshold=2,
            feedback_type="response_quality",  # We're using response_quality
            days=90
        )

        # Count misclassification patterns
        patterns = defaultdict(int)

        for fb in low_feedback:
            if not fb.chat_id:
                continue

            # Get original prediction
            chat = self.db.query(Chat).filter(Chat.id == fb.chat_id).first()
            if not chat or not chat.detected_emotion:
                continue

            predicted = chat.detected_emotion

            # Extract what user said it should be from comment
            correct = self._extract_emotion_from_comment(fb.comment)

            if correct and correct != predicted:
                pattern_key = f"{predicted}→{correct}"
                patterns[pattern_key] += 1

        logger.info(f"Built {len(patterns)} correction patterns from feedback")
        return dict(patterns)

    def _extract_emotion_from_comment(self, comment: Optional[str]) -> Optional[str]:
        """
        Simple keyword extraction from user comments.

        Examples:
        - "I was angry, not sad" → extracts "anger"
        - "This is fear not surprise" → extracts "fear"
        """
        if not comment:
            return None

        comment_lower = comment.lower()

        # Emotion keywords
        emotions = {
            'anger': ['angry', 'mad', 'frustrated', 'annoyed', 'irritated', 'furious'],
            'sadness': ['sad', 'depressed', 'down', 'unhappy', 'miserable', 'upset'],
            'joy': ['happy', 'joyful', 'excited', 'glad', 'cheerful', 'delighted'],
            'fear': ['scared', 'afraid', 'fearful', 'anxious', 'worried', 'nervous'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'startled'],
            'love': ['loving', 'affectionate', 'caring', 'warm', 'tender']
        }

        # Find which emotion user mentioned
        for emotion, keywords in emotions.items():
            for keyword in keywords:
                if keyword in comment_lower:
                    return emotion

        return None

    # ========== ALGORITHM 2: CONFIDENCE ADJUSTMENT ==========

    def calculate_confidence_adjustments(self) -> Dict[str, float]:
        """
        Algorithm: Calculate confidence multipliers for each emotion.

        Logic:
        - High accuracy emotion (avg rating >4) → boost confidence by 10%
        - Low accuracy emotion (avg rating <3) → reduce confidence by 30%

        Returns:
            {
                'anger': 0.7,    # Reduce confidence by 30%
                'joy': 1.1,      # Boost confidence by 10%
                'sadness': 0.85, # Reduce confidence by 15%
                ...
            }
        """
        from ...repositories.feedback_repo import FeedbackRepository
        from ...models.chat import Chat

        repo = FeedbackRepository(self.db)

        # Get all feedback with chat data
        feedback_list = repo.get_user_feedback(
            user_id=None,  # Get all users
            limit=1000,
            feedback_type="response_quality"
        )

        # Calculate average rating per emotion
        emotion_ratings = defaultdict(list)

        for fb in feedback_list:
            if not fb.chat_id:
                continue

            chat = self.db.query(Chat).filter(Chat.id == fb.chat_id).first()
            if chat and chat.detected_emotion:
                emotion_ratings[chat.detected_emotion].append(fb.rating)

        # Calculate adjustments
        adjustments = {}

        for emotion, ratings in emotion_ratings.items():
            if len(ratings) < 5:  # Need at least 5 samples
                continue

            avg_rating = sum(ratings) / len(ratings)

            # Algorithm:
            # Rating 5 (perfect) → 1.1x confidence
            # Rating 4 → 1.0x (no change)
            # Rating 3 → 0.9x
            # Rating 2 → 0.7x
            # Rating 1 → 0.5x

            if avg_rating >= 4.5:
                adjustments[emotion] = 1.1
            elif avg_rating >= 3.5:
                adjustments[emotion] = 1.0
            elif avg_rating >= 2.5:
                adjustments[emotion] = 0.9
            elif avg_rating >= 1.5:
                adjustments[emotion] = 0.7
            else:
                adjustments[emotion] = 0.5

        logger.info(f"Calculated confidence adjustments for {len(adjustments)} emotions")
        return adjustments

    # ========== ALGORITHM 3: CORRECTION APPLICATION ==========

    def apply_bias_reduction(self, text: str, raw_prediction: Dict) -> Dict:
        """
        Main algorithm: Apply all corrections to a prediction.

        Input:
            text: User message
            raw_prediction: {
                'emotion': 'sadness',
                'confidence': 0.87,
                'all_scores': {'sadness': 0.87, 'anger': 0.08, ...}
            }

        Output:
            Corrected prediction with adjusted confidence/emotion
        """
        emotion = raw_prediction.get('emotion', 'neutral')
        confidence = raw_prediction.get('confidence', 0.5)
        all_scores = raw_prediction.get('all_scores', {})

        corrections_applied = []

        # Step 1: Apply confidence adjustment based on historical accuracy
        if emotion in self.confidence_adjustments:
            adjustment = self.confidence_adjustments[emotion]
            original_confidence = confidence
            confidence *= adjustment

            if adjustment != 1.0:
                corrections_applied.append(f"Confidence adjusted {adjustment:.2f}x")
                raw_prediction['confidence_adjusted'] = True
                raw_prediction['adjustment_factor'] = adjustment

        # Step 2: Check for strong correction pattern
        # If this emotion is frequently wrong, switch to corrected emotion
        for pattern, count in self.correction_patterns.items():
            if '→' not in pattern:
                continue

            predicted, correct = pattern.split('→')

            if emotion == predicted and count >= 5:  # Pattern with 5+ cases
                # Switch to corrected emotion if it's plausible
                if correct in all_scores and all_scores[correct] > 0.10:
                    raw_prediction['emotion'] = correct
                    raw_prediction['confidence'] = min(all_scores[correct] * 1.3, 0.95)
                    raw_prediction['corrected'] = True
                    corrections_applied.append(f"Pattern correction: {pattern} ({count} cases)")

                    logger.info(f"Applied pattern correction: {predicted}→{correct}")
                    raw_prediction['corrections_applied'] = corrections_applied
                    return raw_prediction

        # Step 3: If confidence dropped too low, pick second-best emotion
        if confidence < 0.35:
            # Find second-best emotion
            sorted_emotions = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
            if len(sorted_emotions) > 1:
                second_emotion, second_score = sorted_emotions[1]

                # Switch if second-best has reasonable confidence
                if second_score > 0.25:
                    raw_prediction['emotion'] = second_emotion
                    raw_prediction['confidence'] = second_score
                    raw_prediction['corrected'] = True
                    corrections_applied.append("Switched to second-best (low confidence)")

        # Step 4: Apply final confidence adjustment
        raw_prediction['confidence'] = min(max(confidence, 0.1), 0.99)  # Clamp between 10-99%

        if corrections_applied:
            raw_prediction['corrections_applied'] = corrections_applied

        return raw_prediction

    # ========== ALGORITHM 4: CONTEXT-AWARE CORRECTION ==========

    def apply_contextual_correction(self, text: str, emotion: str, confidence: float) -> Dict:
        """
        Algorithm: Use text context to improve prediction.

        Logic:
        - Check for negation words ("not sad" → flip emotion)
        - Check for intensity words ("very happy" → boost confidence)
        - Check for confusion words ("maybe" → reduce confidence)
        """
        text_lower = text.lower()
        corrections = []

        # Negation detection
        negation_words = ['not', 'never', 'no', "don't", "didn't", "isn't", "aren't", "wasn't", "weren't"]
        has_negation = any(f" {word} " in f" {text_lower} " for word in negation_words)

        if has_negation and confidence > 0.6:
            # Reduce confidence for negated statements
            confidence *= 0.75
            corrections.append("Negation detected - reduced confidence")

        # Intensity boosting
        intensity_words = ['very', 'extremely', 'really', 'so', 'absolutely', 'completely', 'totally']
        has_intensity = any(word in text_lower for word in intensity_words)

        if has_intensity:
            confidence = min(confidence * 1.15, 0.99)
            corrections.append("Intensity word detected - boosted confidence")

        # Uncertainty detection
        uncertainty_words = ['maybe', 'perhaps', 'might', 'kinda', 'sort of', 'somewhat', 'not sure']
        has_uncertainty = any(word in text_lower for word in uncertainty_words)

        if has_uncertainty:
            confidence *= 0.85
            corrections.append("Uncertainty detected - reduced confidence")

        return {
            'emotion': emotion,
            'confidence': confidence,
            'context_adjusted': len(corrections) > 0,
            'context_corrections': corrections if corrections else None
        }

    # ========== ALGORITHM 5: ENSEMBLE CORRECTION ==========

    def ensemble_correction(self, text: str, text_emotion: Dict, audio_emotion: Optional[str] = None) -> Dict:
        """
        Algorithm: Combine multiple signals to improve accuracy.

        If you have both text and audio:
        - If they agree → boost confidence
        - If they disagree → use historically more accurate one
        """
        if not audio_emotion:
            return text_emotion

        text_pred = text_emotion['emotion']
        text_conf = text_emotion['confidence']

        # Agreement
        if text_pred == audio_emotion:
            return {
                **text_emotion,
                'confidence': min(text_conf * 1.2, 0.99),  # Boost 20%
                'ensemble_corrected': True,
                'ensemble_reason': 'Text and audio agree'
            }

        # Disagreement - trust the one with historically better accuracy
        text_accuracy = self.confidence_adjustments.get(text_pred, 1.0)
        audio_accuracy = self.confidence_adjustments.get(audio_emotion, 1.0)

        if audio_accuracy > text_accuracy:
            return {
                **text_emotion,
                'emotion': audio_emotion,
                'confidence': text_conf * 0.9,
                'ensemble_corrected': True,
                'ensemble_reason': 'Audio historically more accurate'
            }

        return text_emotion

    # ========== REFRESH MECHANISM ==========

    def refresh(self):
        """
        Rebuild correction patterns and adjustments.
        Call this periodically to incorporate new feedback.
        """
        try:
            self.correction_patterns = self.build_correction_patterns()
            self.confidence_adjustments = self.calculate_confidence_adjustments()
            self.last_refresh = datetime.utcnow()

            logger.info(f"✅ Bias reduction algorithm refreshed. "
                       f"Patterns: {len(self.correction_patterns)}, "
                       f"Adjustments: {len(self.confidence_adjustments)}")
        except Exception as e:
            logger.error(f"❌ Failed to refresh bias algorithm: {e}")

    def get_stats(self) -> Dict:
        """
        Get statistics about the bias reduction system.
        """
        return {
            'correction_patterns': len(self.correction_patterns),
            'confidence_adjustments': len(self.confidence_adjustments),
            'last_refresh': self.last_refresh.isoformat() if self.last_refresh else None,
            'top_patterns': dict(sorted(
                self.correction_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            'emotion_adjustments': self.confidence_adjustments
        }
