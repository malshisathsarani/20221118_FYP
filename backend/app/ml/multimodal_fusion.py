"""
Multi-modal Fusion System
Combines text emotion, speech emotion, and crisis detection into unified mental health assessment
"""
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class MultiModalFusion:
    """
    Fuses multiple emotion analysis models into a comprehensive mental health assessment

    Combines:
    1. Text Emotion Analysis (joy, sadness, anger, fear, love, surprise)
    2. Speech Emotion Analysis (happy, sad, angry, neutral, etc.)
    3. Crisis Detection (trained DistilBERT model)
    """

    def __init__(self):
        """Initialize fusion system with default weights"""
        # Model weights (should sum to 1.0)
        self.weights = {
            'text_emotion': 0.30,      # 30% weight for text emotions
            'speech_emotion': 0.20,    # 20% weight for voice tone
            'crisis_detection': 0.50   # 50% weight for crisis indicators (HIGHEST PRIORITY)
        }

        # Emotion to risk mapping
        self.emotion_risk_map = {
            # High risk emotions (0.7-1.0)
            'sadness': 0.85,
            'fear': 0.80,
            'anger': 0.75,

            # Medium risk emotions (0.3-0.6)
            'surprise': 0.40,
            'neutral': 0.30,

            # Low risk emotions (0.0-0.3)
            'joy': 0.10,
            'love': 0.15,
            'happy': 0.10,
        }

    def fuse(
        self,
        text_emotions: Optional[List[Dict]] = None,
        speech_emotions: Optional[List[Dict]] = None,
        crisis_result: Optional[Dict] = None,
        original_text: str = ""
    ) -> Dict:
        """
        Fuse all emotion analysis results into unified assessment

        Args:
            text_emotions: List of text emotion scores from DistilBERT
                Example: [{'label': 'sadness', 'score': 0.85}, {'label': 'joy', 'score': 0.10}]
            speech_emotions: List of speech emotion scores from Wav2Vec2
                Example: [{'label': 'sad', 'score': 0.78}, {'label': 'neutral', 'score': 0.15}]
            crisis_result: Crisis detection result
                Example: {'is_crisis': True, 'confidence': 0.65}
            original_text: Original message text for context

        Returns:
            Unified mental health assessment with:
                - overall_risk_level: 'none', 'low', 'moderate', 'high', 'critical'
                - risk_score: 0.0-1.0
                - dominant_emotion: Primary detected emotion
                - emotional_state: Human-readable emotional state
                - risk_factors: List of identified risk factors
                - recommendations: List of suggested actions
                - needs_professional_help: Boolean
                - crisis_hotline_suggested: Boolean
        """

        # Calculate individual risk scores
        text_risk = self._calculate_text_emotion_risk(text_emotions)
        speech_risk = self._calculate_speech_emotion_risk(speech_emotions)
        crisis_risk = self._calculate_crisis_risk(crisis_result)

        # Weighted fusion
        overall_risk = (
            self.weights['text_emotion'] * text_risk +
            self.weights['speech_emotion'] * speech_risk +
            self.weights['crisis_detection'] * crisis_risk
        )

        # Cap at 1.0
        overall_risk = min(overall_risk, 1.0)

        # Determine dominant emotion
        dominant_emotion, dominant_score = self._get_dominant_emotion(text_emotions, speech_emotions)

        # Determine emotional state
        emotional_state = self._determine_emotional_state(dominant_emotion, overall_risk)

        # Get risk level
        risk_level = self._classify_risk_level(overall_risk)

        # Collect risk factors
        risk_factors = self._identify_risk_factors(
            text_emotions, speech_emotions, crisis_result, overall_risk
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, dominant_emotion)

        # Build response
        return {
            "overall_risk_level": risk_level,
            "risk_score": round(overall_risk, 4),
            "dominant_emotion": dominant_emotion,
            "dominant_emotion_confidence": round(dominant_score, 4),
            "emotional_state": emotional_state,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "needs_professional_help": risk_level in ['high', 'critical'],
            "crisis_hotline_suggested": risk_level in ['high', 'critical'],
            "component_scores": {
                "text_emotion_risk": round(text_risk, 4),
                "speech_emotion_risk": round(speech_risk, 4),
                "crisis_detection_risk": round(crisis_risk, 4)
            }
        }

    def _calculate_text_emotion_risk(self, text_emotions: Optional[List[Dict]]) -> float:
        """Calculate risk score from text emotions"""
        if not text_emotions or len(text_emotions) == 0:
            return 0.0

        # Get primary emotion (highest score)
        primary = text_emotions[0]
        emotion_label = primary['label'].lower()
        emotion_score = primary['score']

        # Map emotion to risk
        base_risk = self.emotion_risk_map.get(emotion_label, 0.5)

        # Scale by confidence
        return base_risk * emotion_score

    def _calculate_speech_emotion_risk(self, speech_emotions: Optional[List[Dict]]) -> float:
        """Calculate risk score from speech emotions"""
        if not speech_emotions or len(speech_emotions) == 0:
            return 0.0

        # Get primary speech emotion
        primary = speech_emotions[0]
        emotion_label = primary['label'].lower()
        emotion_score = primary['score']

        # Map common speech emotion labels to risk
        speech_risk_map = {
            'angry': 0.75,
            'sad': 0.85,
            'fear': 0.80,
            'disgust': 0.70,
            'happy': 0.10,
            'neutral': 0.30,
            'calm': 0.20,
            'surprised': 0.40
        }

        base_risk = speech_risk_map.get(emotion_label, 0.5)
        return base_risk * emotion_score

    def _calculate_crisis_risk(self, crisis_result: Optional[Dict]) -> float:
        """Calculate risk score from crisis detection"""
        if not crisis_result:
            return 0.0

        is_crisis = crisis_result.get('is_crisis', False)
        confidence = crisis_result.get('confidence', 0.0)

        if is_crisis:
            # Crisis detected - high risk weighted by confidence
            return 0.9 * confidence
        else:
            # No crisis - low risk
            return 0.1 * (1 - confidence)

    def _get_dominant_emotion(
        self,
        text_emotions: Optional[List[Dict]],
        speech_emotions: Optional[List[Dict]]
    ) -> tuple:
        """
        Determine the dominant emotion across all modalities

        Returns:
            Tuple of (emotion_label, confidence_score)
        """
        candidates = []

        if text_emotions and len(text_emotions) > 0:
            candidates.append(text_emotions[0])

        if speech_emotions and len(speech_emotions) > 0:
            candidates.append(speech_emotions[0])

        if not candidates:
            return ("neutral", 0.0)

        # Return emotion with highest score
        dominant = max(candidates, key=lambda x: x['score'])
        return (dominant['label'].lower(), dominant['score'])

    def _determine_emotional_state(self, emotion: str, risk_score: float) -> str:
        """
        Map emotion and risk to human-readable emotional state
        """
        if risk_score >= 0.75:
            return "severe distress"
        elif risk_score >= 0.50:
            if emotion in ['sadness', 'sad']:
                return "depressed"
            elif emotion in ['fear']:
                return "anxious"
            elif emotion in ['anger', 'angry']:
                return "agitated"
            else:
                return "distressed"
        elif risk_score >= 0.25:
            return "mild distress"
        else:
            if emotion in ['joy', 'happy', 'love']:
                return "positive"
            else:
                return "stable"

    def _classify_risk_level(self, risk_score: float) -> str:
        """
        Classify overall risk into categorical level
        """
        if risk_score >= 0.85:
            return "critical"
        elif risk_score >= 0.70:
            return "high"
        elif risk_score >= 0.45:
            return "moderate"
        elif risk_score >= 0.20:
            return "low"
        else:
            return "none"

    def _identify_risk_factors(
        self,
        text_emotions: Optional[List[Dict]],
        speech_emotions: Optional[List[Dict]],
        crisis_result: Optional[Dict],
        overall_risk: float
    ) -> List[str]:
        """
        Identify specific risk factors from analysis results
        """
        factors = []

        # Text emotion factors
        if text_emotions and len(text_emotions) > 0:
            primary = text_emotions[0]
            if primary['label'].lower() in ['sadness', 'fear', 'anger'] and primary['score'] > 0.7:
                factors.append(f"High {primary['label']} in text ({primary['score']:.0%})")

        # Speech emotion factors
        if speech_emotions and len(speech_emotions) > 0:
            primary = speech_emotions[0]
            if primary['label'].lower() in ['sad', 'angry', 'fear'] and primary['score'] > 0.6:
                factors.append(f"Distressed voice tone: {primary['label']} ({primary['score']:.0%})")

        # Crisis detection factors
        if crisis_result and crisis_result.get('is_crisis', False):
            confidence = crisis_result.get('confidence', 0)
            factors.append(f"Crisis indicators detected ({confidence:.0%})")

        # Overall risk factor
        if overall_risk >= 0.70:
            factors.append("Multiple distress indicators across modalities")

        return factors if factors else ["No significant risk factors detected"]

    def _generate_recommendations(self, risk_level: str, emotion: str) -> List[str]:
        """
        Generate context-appropriate recommendations based on risk level and emotion
        """
        recommendations = []

        if risk_level == "critical":
            recommendations = [
                "Immediate intervention required",
                "Contact emergency mental health services",
                "Alert crisis response team",
                "Do not leave user unsupported"
            ]
        elif risk_level == "high":
            recommendations = [
                "Provide crisis hotline information",
                "Suggest professional counseling",
                "Monitor conversation very closely",
                "Offer coping strategies and support resources"
            ]
        elif risk_level == "moderate":
            recommendations = [
                "Monitor conversation closely",
                "Provide mental health resources",
                "Suggest relaxation techniques",
                "Check in frequently"
            ]
        elif risk_level == "low":
            recommendations = [
                "Continue supportive conversation",
                "Provide coping strategies if needed",
                "Monitor for changes in emotional state"
            ]
        else:
            recommendations = [
                "Continue normal conversation",
                "Maintain supportive presence"
            ]

        # Add emotion-specific recommendations
        if emotion in ['sadness', 'sad'] and risk_level in ['moderate', 'high']:
            recommendations.append("Suggest mood-lifting activities")
        elif emotion in ['anger', 'angry'] and risk_level in ['moderate', 'high']:
            recommendations.append("Suggest anger management techniques")
        elif emotion in ['fear'] and risk_level in ['moderate', 'high']:
            recommendations.append("Suggest grounding and breathing exercises")

        return recommendations


# Singleton instance
_fusion_instance = None


def get_multimodal_fusion() -> MultiModalFusion:
    """
    Get or create the singleton fusion system instance
    """
    global _fusion_instance
    if _fusion_instance is None:
        _fusion_instance = MultiModalFusion()
    return _fusion_instance


def analyze_multimodal(
    text_emotions: Optional[List[Dict]] = None,
    speech_emotions: Optional[List[Dict]] = None,
    crisis_result: Optional[Dict] = None,
    original_text: str = ""
) -> Dict:
    """
    Convenience function for multi-modal analysis

    Args:
        text_emotions: Text emotion analysis results
        speech_emotions: Speech emotion analysis results
        crisis_result: Crisis detection results
        original_text: Original message text

    Returns:
        Unified mental health assessment
    """
    fusion = get_multimodal_fusion()
    return fusion.fuse(text_emotions, speech_emotions, crisis_result, original_text)
