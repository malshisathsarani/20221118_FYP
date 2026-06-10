"""
Text Emotion Detection Model
Uses pre-trained DistilBERT model for emotion classification
"""
from transformers import pipeline
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class TextEmotionModel:
    """
    Pre-trained model for text emotion analysis
    Detects emotions: joy, sadness, anger, fear, love, surprise
    """

    def __init__(self, model_name: str = "bhadresh-savani/distilbert-base-uncased-emotion"):
        """
        Initialize the text emotion classifier

        Args:
            model_name: HuggingFace model identifier
        """
        try:
            logger.info(f"Loading text emotion model: {model_name}")
            self.classifier = pipeline(
                "text-classification",
                model=model_name,
                top_k=None  # Return all emotion scores
            )
            logger.info("Text emotion model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load text emotion model: {str(e)}")
            raise

    def predict(self, text: str) -> List[Dict[str, float]]:
        """
        Analyze emotions in text

        Args:
            text: Input text to analyze

        Returns:
            List of dicts with 'label' and 'score' for each emotion
            Example: [{'label': 'joy', 'score': 0.95}, {'label': 'sadness', 'score': 0.02}, ...]
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for emotion analysis")
            return []

        try:
            results = self.classifier(text[:512])[0]  # Limit to 512 chars for model
            # Sort by score descending
            results.sort(key=lambda x: x['score'], reverse=True)
            return results
        except Exception as e:
            logger.error(f"Error analyzing text emotion: {str(e)}")
            return []


# Singleton instance
_model_instance = None


def get_text_emotion_model() -> TextEmotionModel:
    """
    Get or create the singleton text emotion model instance
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = TextEmotionModel()
    return _model_instance
