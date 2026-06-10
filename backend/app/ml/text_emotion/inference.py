"""
Text Emotion Inference Service
Provides high-level API for text emotion analysis
"""
from typing import List, Dict, Optional
from .model import get_text_emotion_model
import logging

logger = logging.getLogger(__name__)


class TextEmotionAnalyzer:
    """
    Service for analyzing emotions in text messages
    """

    def __init__(self):
        self.model = get_text_emotion_model()

    def analyze(self, text: str) -> Dict:
        """
        Analyze emotions in text and return structured results

        Args:
            text: Text message to analyze

        Returns:
            Dict with:
                - primary_emotion: Highest scoring emotion
                - primary_score: Score of primary emotion
                - all_emotions: List of all emotions with scores
                - sentiment: Simplified sentiment (positive/negative/neutral)
        """
        if not text or not text.strip():
            return self._empty_result()

        try:
            emotions = self.model.predict(text)

            if not emotions:
                return self._empty_result()

            # Get primary emotion
            primary = emotions[0]

            # Determine sentiment
            sentiment = self._get_sentiment(primary['label'])

            return {
                "primary_emotion": primary['label'],
                "primary_score": round(primary['score'], 4),
                "all_emotions": [
                    {"label": e['label'], "score": round(e['score'], 4)}
                    for e in emotions
                ],
                "sentiment": sentiment
            }

        except Exception as e:
            logger.error(f"Error in text emotion analysis: {str(e)}")
            return self._empty_result()

    def _get_sentiment(self, emotion: str) -> str:
        """
        Map emotion to simplified sentiment

        Args:
            emotion: Emotion label

        Returns:
            'positive', 'negative', or 'neutral'
        """
        positive_emotions = ['joy', 'love', 'surprise']
        negative_emotions = ['sadness', 'anger', 'fear']

        if emotion in positive_emotions:
            return 'positive'
        elif emotion in negative_emotions:
            return 'negative'
        else:
            return 'neutral'

    def _empty_result(self) -> Dict:
        """
        Return empty result structure
        """
        return {
            "primary_emotion": "neutral",
            "primary_score": 0.0,
            "all_emotions": [],
            "sentiment": "neutral"
        }


# Function for easy import
def analyze_text_emotion(text: str) -> Dict:
    """
    Convenience function to analyze text emotion

    Args:
        text: Text to analyze

    Returns:
        Emotion analysis results
    """
    analyzer = TextEmotionAnalyzer()
    return analyzer.analyze(text)
