"""
Speech Emotion Recognition Model
Uses pre-trained Wav2Vec2 model for audio emotion classification
"""
from transformers import pipeline
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SpeechEmotionModel:
    """
    Pre-trained model for speech emotion recognition
    Analyzes emotional tone from audio files
    """

    def __init__(self, model_name: str = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"):
        """
        Initialize the speech emotion classifier

        Args:
            model_name: HuggingFace model identifier for speech emotion
        """
        try:
            logger.info(f"Loading speech emotion model: {model_name}")
            self.classifier = pipeline(
                "audio-classification",
                model=model_name
            )
            logger.info("Speech emotion model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load speech emotion model: {str(e)}")
            raise

    def predict(self, audio_path: str) -> List[Dict[str, float]]:
        """
        Analyze emotions in audio file

        Args:
            audio_path: Path to audio file (wav, mp3, etc.)

        Returns:
            List of dicts with 'label' and 'score' for each emotion
            Example: [{'label': 'happy', 'score': 0.85}, {'label': 'neutral', 'score': 0.10}, ...]
        """
        if not audio_path:
            logger.warning("No audio path provided")
            return []

        try:
            results = self.classifier(audio_path, top_k=None)
            # Sort by score descending
            results.sort(key=lambda x: x['score'], reverse=True)
            return results
        except Exception as e:
            logger.error(f"Error analyzing speech emotion: {str(e)}")
            return []


# Singleton instance
_model_instance = None


def get_speech_emotion_model() -> SpeechEmotionModel:
    """
    Get or create the singleton speech emotion model instance
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = SpeechEmotionModel()
    return _model_instance
