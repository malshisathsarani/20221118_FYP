"""
Crisis Detection Inference Service
Provides high-level API for crisis risk assessment
"""
from typing import Dict, Optional, List
from .model import get_crisis_detection_model
import logging

logger = logging.getLogger(__name__)


class CrisisDetector:
    """
    Service for detecting mental health crisis situations
    """

    def __init__(self):
        self.model = get_crisis_detection_model()

    def assess_risk(
        self,
        text_emotion: Dict,
        speech_emotion: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Assess crisis risk based on multimodal emotion analysis

        Args:
            text_emotion: Text emotion analysis results
            speech_emotion: Speech emotion analysis results (optional)
            conversation_history: Recent conversation context (optional)

        Returns:
            Crisis risk assessment with risk level and recommendations
        """
        try:
            risk_assessment = self.model.predict_risk(
                text_emotion=text_emotion,
                speech_emotion=speech_emotion,
                conversation_history=conversation_history
            )

            # Add emergency resources if high risk
            if risk_assessment['risk_level'] in ['high', 'critical']:
                risk_assessment['emergency_resources'] = self._get_emergency_resources()

            return risk_assessment

        except Exception as e:
            logger.error(f"Error in crisis risk assessment: {str(e)}")
            return self._safe_default_response()

    def _get_emergency_resources(self) -> List[Dict]:
        """
        Get emergency mental health resources

        Returns:
            List of emergency contact resources
        """
        return [
            {
                "name": "National Suicide Prevention Lifeline",
                "phone": "988",
                "available": "24/7",
                "description": "Free and confidential support"
            },
            {
                "name": "Crisis Text Line",
                "text": "HOME to 741741",
                "available": "24/7",
                "description": "Text-based crisis support"
            },
            {
                "name": "Emergency Services",
                "phone": "911",
                "available": "24/7",
                "description": "For immediate life-threatening situations"
            }
        ]

    def _safe_default_response(self) -> Dict:
        """
        Return safe default response in case of errors
        """
        return {
            "risk_level": "unknown",
            "risk_score": 0.0,
            "risk_factors": ["Error in assessment"],
            "recommended_action": "monitor_closely",
            "needs_professional_help": True,
            "emergency_resources": self._get_emergency_resources()
        }


# Function for easy import
def detect_crisis(
    text_emotion: Dict,
    speech_emotion: Optional[Dict] = None,
    conversation_history: Optional[List[Dict]] = None
) -> Dict:
    """
    Convenience function to detect crisis risk

    Args:
        text_emotion: Text emotion analysis
        speech_emotion: Speech emotion analysis (optional)
        conversation_history: Conversation context (optional)

    Returns:
        Crisis risk assessment
    """
    detector = CrisisDetector()
    return detector.assess_risk(text_emotion, speech_emotion, conversation_history)
