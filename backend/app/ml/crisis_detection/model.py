"""
Crisis Detection Model
Trained DistilBERT model for detecting mental health crisis situations
"""
from typing import Dict, Optional
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import logging
import os

logger = logging.getLogger(__name__)


class CrisisDetectionModel:
    """
    Trained DistilBERT model for detecting crisis situations from text
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize crisis detection model

        Args:
            model_path: Path to trained model directory
        """
        if model_path is None:
            # Default path to trained model (Model 2: 97.16% accuracy, 98.16% recall)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "crisis_detector_model_2")

        self.model_path = model_path
        self.threshold_high_risk = 0.75
        self.threshold_moderate_risk = 0.50

        try:
            logger.info(f"Loading crisis detection model from: {model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
            self.model.eval()  # Set to evaluation mode

            # Use GPU if available
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)

            logger.info(f"✓ Crisis detection model loaded successfully on {self.device}")
            logger.info(f"✓ Model path: {model_path}")
            logger.info(f"✓ High-risk threshold: {self.threshold_high_risk}, Moderate-risk threshold: {self.threshold_moderate_risk}")
        except Exception as e:
            logger.error(f"Failed to load trained model: {str(e)}")
            logger.warning("Falling back to rule-based detection")
            self.model = None
            self.tokenizer = None

    def predict_crisis_from_text(self, text: str) -> Dict:
        """
        Predict if text indicates a crisis using trained model

        Args:
            text: Input text to analyze

        Returns:
            Dict with is_crisis (bool) and confidence (float)
        """
        if not text or not text.strip():
            return {"is_crisis": False, "confidence": 0.0}

        # Use trained ML model (Model 2: 97.16% accuracy, 98.16% recall!)
        if self.model is None or self.tokenizer is None:
            # Fallback to rule-based if model not loaded
            logger.warning("ML model not loaded, using rule-based fallback")
            return self._rule_based_crisis_detection(text)

        try:
            # Tokenize input (using max_length=128 from model 2 config)
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=128,
                padding=True
            ).to(self.device)

            # Get prediction from trained model
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)
                prediction = torch.argmax(probs, dim=-1).item()
                confidence = probs[0][prediction].item()

                # Log for debugging
                logger.info(f"Crisis detection - Text: '{text}'")
                logger.info(f"Crisis detection - Logits: {outputs.logits}")
                logger.info(f"Crisis detection - Probabilities: {probs}")
                logger.info(f"Crisis detection - Prediction: {prediction}, Confidence: {confidence}")

            return {
                "is_crisis": bool(prediction == 1),
                "confidence": float(confidence)
            }
        except Exception as e:
            logger.error(f"Error in crisis prediction: {str(e)}")
            return {"is_crisis": False, "confidence": 0.0}

    def _rule_based_crisis_detection(self, text: str) -> Dict:
        """
        Simple rule-based crisis detection as fallback
        """
        crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'want to die',
            'no point living', 'hopeless', 'give up', 'can\'t go on'
        ]

        text_lower = text.lower()
        is_crisis = any(keyword in text_lower for keyword in crisis_keywords)
        confidence = 0.7 if is_crisis else 0.3

        return {"is_crisis": is_crisis, "confidence": confidence}

    def predict_risk(
        self,
        text_emotion: Dict,
        speech_emotion: Optional[Dict] = None,
        conversation_history: Optional[list] = None
    ) -> Dict:
        """
        Predict crisis risk level based on emotion analysis

        Args:
            text_emotion: Results from text emotion analysis
            speech_emotion: Results from speech emotion analysis (optional)
            conversation_history: Recent messages for context (optional)

        Returns:
            Dict with:
                - risk_level: 'none', 'low', 'moderate', 'high', 'critical'
                - risk_score: Float between 0-1
                - risk_factors: List of identified risk factors
                - recommended_action: Suggested intervention
        """
        risk_score = 0.0
        risk_factors = []

        # Get text from emotion analysis or use primary emotion
        text_for_crisis = text_emotion.get('original_text', '')

        # Use trained model for crisis detection
        if text_for_crisis:
            logger.info(f"Analyzing crisis for text: '{text_for_crisis}'")
            crisis_result = self.predict_crisis_from_text(text_for_crisis)
            logger.info(f"Crisis detection result: {crisis_result}")
            if crisis_result['is_crisis']:
                risk_score += crisis_result['confidence'] * 0.6  # 60% weight for crisis detection
                risk_factors.append(f"Crisis indicators detected (confidence: {crisis_result['confidence']:.2%})")
        else:
            logger.warning("No text available for crisis detection")

        # Analyze text emotion (30% weight)
        if text_emotion:
            primary_emotion = text_emotion.get('primary_emotion', '')
            emotion_score = text_emotion.get('primary_score', 0)

            # High-risk emotions
            if primary_emotion in ['sadness', 'fear', 'anger'] and emotion_score > 0.7:
                risk_score += 0.3 * emotion_score
                risk_factors.append(f"High {primary_emotion} detected ({emotion_score:.2%})")

        # Analyze speech emotion (10% weight if available)
        if speech_emotion:
            speech_emotion_label = speech_emotion.get('primary_emotion', '')
            speech_score = speech_emotion.get('primary_score', 0)

            if any(neg in speech_emotion_label.lower() for neg in ['sad', 'stress', 'angry']) and speech_score > 0.6:
                risk_score += 0.1 * speech_score
                risk_factors.append(f"Distressed voice tone detected ({speech_score:.2%})")

        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)

        # Determine risk level
        if risk_score >= self.threshold_high_risk:
            risk_level = 'high'
            action = 'immediate_intervention'
        elif risk_score >= self.threshold_moderate_risk:
            risk_level = 'moderate'
            action = 'monitor_closely'
        elif risk_score >= 0.25:
            risk_level = 'low'
            action = 'continue_conversation'
        else:
            risk_level = 'none'
            action = 'normal_conversation'

        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 4),
            "risk_factors": risk_factors,
            "recommended_action": action,
            "needs_professional_help": risk_level in ['high', 'critical']
        }


# Singleton instance
_model_instance = None


def get_crisis_detection_model() -> CrisisDetectionModel:
    """
    Get or create the singleton crisis detection model instance
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = CrisisDetectionModel()
    return _model_instance
