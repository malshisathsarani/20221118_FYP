"""
Speech Emotion Inference Service
Provides high-level API for audio emotion analysis
"""
from typing import Dict, Optional
from pathlib import Path
from .model import get_speech_emotion_model
import logging

logger = logging.getLogger(__name__)


class SpeechEmotionAnalyzer:
    """
    Service for analyzing emotions in audio recordings
    """

    def __init__(self):
        self.model = get_speech_emotion_model()

    def analyze(self, audio_path: str) -> Dict:
        """
        Analyze emotions in audio file and return structured results

        Args:
            audio_path: Path to audio file

        Returns:
            Dict with:
                - primary_emotion: Highest scoring emotion
                - primary_score: Score of primary emotion
                - all_emotions: List of all emotions with scores
                - sentiment: Simplified sentiment (positive/negative/neutral)
        """
        if not audio_path or not Path(audio_path).exists():
            logger.warning(f"Invalid audio path: {audio_path}")
            return self._empty_result()

        try:
            emotions = self.model.predict(audio_path)

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
            logger.error(f"Error in speech emotion analysis: {str(e)}")
            return self._empty_result()

    def _get_sentiment(self, emotion: str) -> str:
        """
        Map emotion to simplified sentiment

        Args:
            emotion: Emotion label

        Returns:
            'positive', 'negative', or 'neutral'
        """
        emotion_lower = emotion.lower()

        positive_emotions = ['happy', 'excited', 'joy', 'calm', 'love']
        negative_emotions = ['sad', 'angry', 'fear', 'disgust', 'stress']

        if any(pos in emotion_lower for pos in positive_emotions):
            return 'positive'
        elif any(neg in emotion_lower for neg in negative_emotions):
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
def analyze_speech_emotion(audio_path: str) -> Dict:
    """
    Convenience function to analyze speech emotion

    Args:
        audio_path: Path to audio file

    Returns:
        Emotion analysis results
    """
    analyzer = SpeechEmotionAnalyzer()
    return analyzer.analyze(audio_path)
