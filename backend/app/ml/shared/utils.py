"""
Shared ML Utilities
Common functions for preprocessing, validation, and integration
"""
from typing import Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and preprocess text for emotion analysis

    Args:
        text: Raw text input

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def validate_audio_file(file_path: str) -> bool:
    """
    Validate audio file exists and has valid format

    Args:
        file_path: Path to audio file

    Returns:
        True if valid, False otherwise
    """
    import os

    if not file_path or not os.path.exists(file_path):
        return False

    # Check file extension
    valid_extensions = ['.wav', '.mp3', '.m4a', '.ogg', '.flac']
    ext = os.path.splitext(file_path)[1].lower()

    return ext in valid_extensions


def combine_emotion_scores(
    text_emotion: Dict,
    speech_emotion: Optional[Dict] = None,
    text_weight: float = 0.5,
    speech_weight: float = 0.5
) -> Dict:
    """
    Combine text and speech emotion scores using weighted average

    Args:
        text_emotion: Text emotion analysis results
        speech_emotion: Speech emotion analysis results (optional)
        text_weight: Weight for text emotion (0-1)
        speech_weight: Weight for speech emotion (0-1)

    Returns:
        Combined emotion scores
    """
    if not speech_emotion or not speech_emotion.get('all_emotions'):
        # Only text emotion available
        return text_emotion

    # Normalize weights
    total_weight = text_weight + speech_weight
    text_weight /= total_weight
    speech_weight /= total_weight

    # Create emotion score mappings
    text_scores = {
        e['emotion']: e['score']
        for e in text_emotion.get('all_emotions', [])
    }

    speech_scores = {
        e['emotion']: e['score']
        for e in speech_emotion.get('all_emotions', [])
    }

    # Combine scores
    all_emotions = set(text_scores.keys()) | set(speech_scores.keys())
    combined_scores = []

    for emotion in all_emotions:
        text_score = text_scores.get(emotion, 0.0)
        speech_score = speech_scores.get(emotion, 0.0)

        combined_score = (text_weight * text_score) + (speech_weight * speech_score)

        combined_scores.append({
            "emotion": emotion,
            "score": round(combined_score, 4)
        })

    # Sort by score
    combined_scores.sort(key=lambda x: x['score'], reverse=True)

    # Get primary emotion
    primary = combined_scores[0] if combined_scores else {"emotion": "neutral", "score": 0.0}

    # Determine sentiment
    sentiment = _determine_sentiment(primary['emotion'])

    return {
        "primary_emotion": primary['emotion'],
        "primary_score": primary['score'],
        "all_emotions": combined_scores,
        "sentiment": sentiment,
        "is_multimodal": True
    }


def _determine_sentiment(emotion: str) -> str:
    """
    Determine sentiment from emotion label

    Args:
        emotion: Emotion label

    Returns:
        'positive', 'negative', or 'neutral'
    """
    emotion_lower = emotion.lower()

    positive = ['joy', 'happy', 'love', 'excited', 'calm', 'surprise']
    negative = ['sad', 'angry', 'fear', 'disgust', 'stress', 'sadness', 'anger']

    if any(pos in emotion_lower for pos in positive):
        return 'positive'
    elif any(neg in emotion_lower for neg in negative):
        return 'negative'
    else:
        return 'neutral'


def format_emotion_response(
    text_emotion: Dict,
    speech_emotion: Optional[Dict] = None,
    crisis_assessment: Optional[Dict] = None
) -> Dict:
    """
    Format complete emotion analysis response

    Args:
        text_emotion: Text emotion analysis
        speech_emotion: Speech emotion analysis (optional)
        crisis_assessment: Crisis risk assessment (optional)

    Returns:
        Formatted response for API
    """
    response = {
        "text_emotion": text_emotion,
        "timestamp": None  # Add timestamp in service layer
    }

    if speech_emotion:
        response["speech_emotion"] = speech_emotion
        response["combined_emotion"] = combine_emotion_scores(text_emotion, speech_emotion)

    if crisis_assessment:
        response["crisis_assessment"] = crisis_assessment

    return response
