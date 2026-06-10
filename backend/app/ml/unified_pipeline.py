"""
Unified ML Pipeline Orchestrator
Coordinates all ML models and multi-modal fusion for comprehensive mental health assessment
"""
from typing import Dict, Optional, List
import logging
from .text_emotion.inference import TextEmotionAnalyzer
from .speech_emotion.inference import SpeechEmotionAnalyzer
from .crisis_detection.inference import CrisisDetector
from .multimodal_fusion import get_multimodal_fusion, MultiModalFusion

logger = logging.getLogger(__name__)


class UnifiedMLPipeline:
    """
    Unified ML Pipeline that orchestrates:
    1. Text emotion analysis (DistilBERT)
    2. Speech emotion analysis (Wav2Vec2)
    3. Crisis detection (trained DistilBERT)
    4. Multi-modal fusion for comprehensive assessment
    """

    def __init__(self):
        """Initialize all ML models and fusion system"""
        logger.info("Initializing Unified ML Pipeline...")

        # Initialize individual models
        self.text_emotion_analyzer = self._init_text_analyzer()
        self.speech_emotion_analyzer = self._init_speech_analyzer()
        self.crisis_detector = self._init_crisis_detector()

        # Initialize fusion system
        self.fusion_system = get_multimodal_fusion()

        logger.info("✓ Unified ML Pipeline initialized successfully")

    def _init_text_analyzer(self) -> Optional[TextEmotionAnalyzer]:
        """Initialize text emotion analyzer"""
        try:
            analyzer = TextEmotionAnalyzer()
            logger.info("✓ Text emotion analyzer loaded")
            return analyzer
        except Exception as e:
            logger.error(f"Failed to load text emotion analyzer: {e}")
            return None

    def _init_speech_analyzer(self) -> Optional[SpeechEmotionAnalyzer]:
        """Initialize speech emotion analyzer"""
        try:
            analyzer = SpeechEmotionAnalyzer()
            logger.info("✓ Speech emotion analyzer loaded")
            return analyzer
        except Exception as e:
            logger.error(f"Failed to load speech emotion analyzer: {e}")
            return None

    def _init_crisis_detector(self) -> Optional[CrisisDetector]:
        """Initialize crisis detector"""
        try:
            detector = CrisisDetector()
            logger.info("✓ Crisis detector loaded")
            return detector
        except Exception as e:
            logger.error(f"Failed to load crisis detector: {e}")
            return None

    def analyze_comprehensive(
        self,
        text: str,
        audio_path: Optional[str] = None
    ) -> Dict:
        """
        Comprehensive mental health analysis using all available modalities

        Args:
            text: User message text
            audio_path: Optional path to audio file

        Returns:
            Complete assessment including:
                - text_emotion: Text emotion analysis results
                - speech_emotion: Speech emotion analysis results (if audio provided)
                - crisis_assessment: Crisis detection results
                - fusion_result: Multi-modal fusion assessment
                - recommendations: Suggested actions
        """
        logger.info(f"Running comprehensive analysis - Text: {len(text)} chars, Audio: {audio_path is not None}")

        # Step 1: Analyze text emotion
        text_emotion_result = self._analyze_text_emotion(text)

        # Step 2: Analyze speech emotion (if audio provided)
        speech_emotion_result = None
        if audio_path:
            speech_emotion_result = self._analyze_speech_emotion(audio_path)

        # Step 3: Detect crisis
        crisis_result = self._detect_crisis(text, text_emotion_result)

        # Step 4: Multi-modal fusion
        fusion_result = self._fuse_modalities(
            text_emotion_result,
            speech_emotion_result,
            crisis_result,
            text
        )

        # Build comprehensive result
        return {
            "text_emotion": text_emotion_result,
            "speech_emotion": speech_emotion_result,
            "crisis_assessment": crisis_result,
            "fusion_result": fusion_result,
            "recommendations": self._generate_recommendations(fusion_result),
            "pipeline_status": "success"
        }

    def _analyze_text_emotion(self, text: str) -> Dict:
        """Analyze text emotion using DistilBERT"""
        if not self.text_emotion_analyzer:
            logger.warning("Text emotion analyzer not available")
            return self._fallback_text_emotion()

        try:
            result = self.text_emotion_analyzer.analyze(text)

            # Format for fusion system
            all_emotions = result.get('all_emotions', [])

            return {
                "primary_emotion": result.get('primary_emotion'),
                "primary_score": result.get('primary_score'),
                "all_emotions": all_emotions,
                "sentiment": result.get('sentiment'),
                "model": "DistilBERT",
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error analyzing text emotion: {e}")
            return self._fallback_text_emotion()

    def _analyze_speech_emotion(self, audio_path: str) -> Dict:
        """Analyze speech emotion using Wav2Vec2"""
        if not self.speech_emotion_analyzer:
            logger.warning("Speech emotion analyzer not available")
            return self._fallback_speech_emotion()

        try:
            result = self.speech_emotion_analyzer.analyze(audio_path)

            # Format for fusion system
            all_emotions = result.get('all_emotions', [])

            return {
                "primary_emotion": result.get('primary_emotion'),
                "primary_score": result.get('primary_score'),
                "all_emotions": all_emotions,
                "sentiment": result.get('sentiment'),
                "model": "Wav2Vec2",
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error analyzing speech emotion: {e}")
            return self._fallback_speech_emotion()

    def _detect_crisis(self, text: str, text_emotion_result: Dict) -> Dict:
        """Detect crisis using trained DistilBERT model"""
        if not self.crisis_detector:
            logger.warning("Crisis detector not available")
            return self._fallback_crisis_detection(text)

        try:
            # Add original text to emotion result for crisis detection
            text_emotion_with_text = {**text_emotion_result, 'original_text': text}

            # Use the trained model for crisis detection
            result = self.crisis_detector.assess_risk(text_emotion=text_emotion_with_text)

            return {
                "is_crisis": result.get('needs_professional_help', False),
                "confidence": result.get('risk_score', 0.0),
                "risk_level": result.get('risk_level'),
                "risk_factors": result.get('risk_factors', []),
                "recommended_action": result.get('recommended_action'),
                "emergency_resources": result.get('emergency_resources'),
                "model": "DistilBERT (trained)",
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error detecting crisis: {e}")
            return self._fallback_crisis_detection(text)

    def _fuse_modalities(
        self,
        text_emotion: Dict,
        speech_emotion: Optional[Dict],
        crisis_result: Dict,
        original_text: str
    ) -> Dict:
        """Fuse all modality results using multi-modal fusion"""
        try:
            # Prepare data for fusion system
            text_emotions = text_emotion.get('all_emotions', [])
            speech_emotions = speech_emotion.get('all_emotions', []) if speech_emotion else None

            # Run fusion
            fusion_result = self.fusion_system.fuse(
                text_emotions=text_emotions,
                speech_emotions=speech_emotions,
                crisis_result=crisis_result,
                original_text=original_text
            )

            return fusion_result
        except Exception as e:
            logger.error(f"Error in multi-modal fusion: {e}")
            return self._fallback_fusion(text_emotion, crisis_result)

    def _generate_recommendations(self, fusion_result: Dict) -> List[str]:
        """Generate comprehensive recommendations based on fusion result"""
        recommendations = fusion_result.get('recommendations', [])

        # Add additional context-specific recommendations
        risk_level = fusion_result.get('overall_risk_level', 'none')

        if risk_level == 'critical':
            recommendations.insert(0, "🚨 IMMEDIATE ACTION REQUIRED")
        elif risk_level == 'high':
            recommendations.insert(0, "⚠️ HIGH PRIORITY - Close monitoring needed")

        return recommendations

    # Fallback methods
    def _fallback_text_emotion(self) -> Dict:
        """Fallback when text emotion analyzer unavailable"""
        return {
            "primary_emotion": "neutral",
            "primary_score": 0.0,
            "all_emotions": [{"label": "neutral", "score": 1.0}],
            "sentiment": "neutral",
            "model": "fallback",
            "status": "fallback"
        }

    def _fallback_speech_emotion(self) -> Dict:
        """Fallback when speech emotion analyzer unavailable"""
        return {
            "primary_emotion": "neutral",
            "primary_score": 0.0,
            "all_emotions": [{"label": "neutral", "score": 1.0}],
            "sentiment": "neutral",
            "model": "fallback",
            "status": "fallback"
        }

    def _fallback_crisis_detection(self, text: str) -> Dict:
        """Fallback crisis detection using keyword matching"""
        crisis_keywords = [
            "suicide", "kill myself", "end it all", "want to die",
            "no point", "hopeless", "worthless", "can't go on"
        ]

        text_lower = text.lower()
        detected_keywords = [kw for kw in crisis_keywords if kw in text_lower]

        crisis_score = min(len(detected_keywords) * 0.3, 1.0)
        is_crisis = crisis_score > 0.5

        return {
            "is_crisis": is_crisis,
            "confidence": crisis_score,
            "risk_level": "high" if is_crisis else "low",
            "risk_factors": detected_keywords if detected_keywords else [],
            "model": "fallback (keyword-based)",
            "status": "fallback"
        }

    def _fallback_fusion(self, text_emotion: Dict, crisis_result: Dict) -> Dict:
        """Fallback fusion when fusion system fails"""
        risk_score = crisis_result.get('confidence', 0.0)

        return {
            "overall_risk_level": "moderate" if risk_score > 0.5 else "low",
            "risk_score": risk_score,
            "dominant_emotion": text_emotion.get('primary_emotion', 'neutral'),
            "dominant_emotion_confidence": text_emotion.get('primary_score', 0.0),
            "emotional_state": "unknown",
            "risk_factors": crisis_result.get('risk_factors', []),
            "recommendations": ["Unable to perform full analysis", "Continue monitoring"],
            "needs_professional_help": crisis_result.get('is_crisis', False),
            "crisis_hotline_suggested": crisis_result.get('is_crisis', False),
            "status": "fallback"
        }

    def get_pipeline_status(self) -> Dict:
        """Get status of all pipeline components"""
        return {
            "pipeline": "Unified ML Pipeline",
            "components": {
                "text_emotion_analyzer": {
                    "loaded": self.text_emotion_analyzer is not None,
                    "model": "DistilBERT (HuggingFace)"
                },
                "speech_emotion_analyzer": {
                    "loaded": self.speech_emotion_analyzer is not None,
                    "model": "Wav2Vec2 (HuggingFace)"
                },
                "crisis_detector": {
                    "loaded": self.crisis_detector is not None,
                    "model": "DistilBERT (trained)"
                },
                "fusion_system": {
                    "loaded": self.fusion_system is not None,
                    "algorithm": "Weighted Multi-Modal Fusion"
                }
            },
            "all_systems_operational": all([
                self.text_emotion_analyzer,
                self.speech_emotion_analyzer,
                self.crisis_detector,
                self.fusion_system
            ])
        }


# Singleton instance
_pipeline_instance = None


def get_unified_pipeline() -> UnifiedMLPipeline:
    """
    Get or create the singleton unified pipeline instance

    Returns:
        UnifiedMLPipeline instance
    """
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = UnifiedMLPipeline()
    return _pipeline_instance
