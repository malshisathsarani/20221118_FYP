from sqlalchemy.orm import Session
from typing import Optional, Dict
from ..repositories.chat_repo import ChatRepository
from ..ml.unified_pipeline import get_unified_pipeline
from ..schemas.chat import ChatRequest, ChatResponse, EmotionAnalysis, CrisisDetection
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Service layer for chat-related business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.ml_pipeline = get_unified_pipeline()

    def process_message(self, user_id: int, chat_request: ChatRequest) -> ChatResponse:
        """Process a chat message with comprehensive ML analysis using unified pipeline"""
        try:
            # Run comprehensive analysis through unified pipeline
            analysis = self.ml_pipeline.analyze_comprehensive(
                text=chat_request.message,
                audio_path=chat_request.audio_data  # Will be file path when audio is uploaded
            )

            # Extract results
            text_emotion = analysis.get('text_emotion', {})
            speech_emotion = analysis.get('speech_emotion')
            crisis_assessment = analysis.get('crisis_assessment', {})
            fusion_result = analysis.get('fusion_result', {})

            # Generate response based on fusion result
            response_text = self._generate_response(
                message=chat_request.message,
                fusion_result=fusion_result,
                crisis_assessment=crisis_assessment
            )

            # Map fusion risk level to database crisis level
            risk_level = fusion_result.get('overall_risk_level', 'none')
            is_crisis = self._map_risk_to_crisis_level(risk_level)

            # Extract emotion scores
            all_emotion_scores = {}
            for emotion_item in text_emotion.get('all_emotions', []):
                all_emotion_scores[emotion_item.get('label')] = emotion_item.get('score')

            # Save to database
            chat = self.chat_repo.create(
                user_id=user_id,
                session_id=chat_request.session_id,
                message=chat_request.message,
                response=response_text,
                detected_emotion=fusion_result.get('dominant_emotion'),
                emotion_confidence=fusion_result.get('dominant_emotion_confidence', 0.0),
                emotion_scores=all_emotion_scores,
                audio_emotion=speech_emotion.get('primary_emotion') if speech_emotion else None,
                audio_confidence=speech_emotion.get('primary_score') if speech_emotion else None,
                crisis_score=fusion_result.get('risk_score', 0.0),
                is_crisis=is_crisis
            )

            # Build response with full analysis
            return self._build_chat_response(
                chat,
                text_emotion=text_emotion,
                fusion_result=fusion_result,
                crisis_assessment=crisis_assessment
            )

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing message: {str(e)}"
            )

    def _map_risk_to_crisis_level(self, risk_level: str) -> int:
        """Map fusion risk level to database crisis level integer"""
        risk_map = {
            'none': 0,
            'low': 0,
            'moderate': 1,
            'high': 2,
            'critical': 3
        }
        return risk_map.get(risk_level, 0)

    def _generate_response(
        self,
        message: str,
        fusion_result: Dict,
        crisis_assessment: Dict
    ) -> str:
        """
        Generate appropriate response based on fusion analysis

        Uses multi-modal fusion result to create empathetic, context-aware response
        """
        risk_level = fusion_result.get('overall_risk_level', 'none')
        dominant_emotion = fusion_result.get('dominant_emotion', 'neutral')
        emotional_state = fusion_result.get('emotional_state', 'stable')

        # Critical/High risk responses
        if risk_level in ['critical', 'high']:
            return (
                f"I'm really concerned about what you're going through. Your feelings are important, "
                f"and I can see you're experiencing {emotional_state}. I want you to know that help is available. "
                f"Please consider reaching out to a mental health professional immediately or calling the "
                f"National Suicide Prevention Lifeline at 988. You don't have to face this alone. "
                f"Would you like me to provide additional support resources?"
            )

        # Moderate risk responses
        if risk_level == 'moderate':
            emotion_responses = {
                'sadness': "I hear that you're feeling down, and it seems like you're going through a difficult time. It's okay to feel this way.",
                'fear': "It sounds like you're feeling anxious or worried. Those feelings are completely valid.",
                'anger': "I understand you're feeling frustrated or upset. It's natural to have these feelings.",
            }

            base_response = emotion_responses.get(
                dominant_emotion,
                f"I can see you're experiencing {emotional_state}."
            )

            return (
                f"{base_response} Would you like to talk more about what's troubling you? "
                f"I'm here to listen and support you. If things feel overwhelming, please don't "
                f"hesitate to reach out to a counselor or therapist."
            )

        # Low risk / Normal conversation
        emotion_responses = {
            'sadness': "I hear that you're feeling down. It's okay to feel sad sometimes. What's on your mind?",
            'fear': "It sounds like something is worrying you. Let's talk about it. What's concerning you?",
            'anger': "I understand you're feeling frustrated. Those feelings are valid. What's bothering you?",
            'joy': "I'm glad to hear you're feeling positive! What's been going well for you?",
            'love': "It's wonderful that you're feeling good. Tell me more about what's making you happy.",
            'surprise': "It sounds like something unexpected happened. Would you like to share more?",
            'neutral': "I'm here to listen and support you. How are you feeling today?"
        }

        return emotion_responses.get(dominant_emotion, emotion_responses['neutral'])

    def get_chat_history(self, user_id: int, session_id: Optional[str] = None, limit: int = 50):
        """Get chat history for user"""
        if session_id:
            chats = self.chat_repo.get_by_session(session_id, limit)
        else:
            chats = self.chat_repo.get_by_user(user_id, limit)

        return {
            "chats": [self._build_chat_response(chat) for chat in chats],
            "total": len(chats),
            "session_id": session_id
        }

    def get_user_sessions(self, user_id: int):
        """Get all session IDs for a user"""
        return self.chat_repo.get_user_sessions(user_id)

    def create_session(self, user_id: int) -> str:
        """
        Create a new chat session ID.

        Returns a unique session ID for starting a new conversation.
        Session ID format: user_{user_id}_{timestamp}
        """
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        session_id = f"user_{user_id}_{timestamp}"
        return session_id

    def get_session_info(self, session_id: str, user_id: int):
        """
        Get information about a specific chat session.

        Returns session metadata including message count, emotion summary, etc.
        """
        chats = self.chat_repo.get_by_session(session_id)

        # Filter to ensure user owns this session
        user_chats = [chat for chat in chats if chat.user_id == user_id]

        if not user_chats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or access denied"
            )

        # Calculate session statistics
        emotions = [chat.detected_emotion for chat in user_chats if chat.detected_emotion]
        crisis_count = sum(1 for chat in user_chats if chat.is_crisis > 0)

        # Get dominant emotion
        dominant_emotion = None
        if emotions:
            from collections import Counter
            emotion_counts = Counter(emotions)
            dominant_emotion = emotion_counts.most_common(1)[0][0]

        return {
            "session_id": session_id,
            "user_id": user_id,
            "message_count": len(user_chats),
            "dominant_emotion": dominant_emotion,
            "crisis_alerts": crisis_count,
            "first_message_at": user_chats[0].created_at if user_chats else None,
            "last_message_at": user_chats[-1].created_at if user_chats else None
        }

    def delete_session(self, session_id: str, user_id: int) -> bool:
        """
        Delete all messages in a chat session.

        Only allows deletion if user owns the session.
        """
        chats = self.chat_repo.get_by_session(session_id)

        # Verify ownership
        if not all(chat.user_id == user_id for chat in chats):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete session - access denied"
            )

        # Delete all chats in session
        for chat in chats:
            self.db.delete(chat)

        self.db.commit()
        return True

    def _build_chat_response(
        self,
        chat,
        text_emotion: Optional[Dict] = None,
        fusion_result: Optional[Dict] = None,
        crisis_assessment: Optional[Dict] = None
    ) -> ChatResponse:
        """Build comprehensive chat response object with fusion analysis"""
        emotion_analysis = None
        if chat.detected_emotion:
            emotion_analysis = EmotionAnalysis(
                emotion=chat.detected_emotion,
                confidence=chat.emotion_confidence or 0.0,
                all_scores=chat.emotion_scores or {}
            )

        crisis_detection = None
        if chat.is_crisis > 0:
            severity_map = {0: None, 1: "moderate", 2: "high", 3: "critical"}

            # Get indicators from crisis assessment or fusion result
            indicators = []
            if crisis_assessment:
                indicators = crisis_assessment.get('risk_factors', [])
            elif fusion_result:
                indicators = fusion_result.get('risk_factors', [])

            crisis_detection = CrisisDetection(
                is_crisis=True,
                severity=severity_map.get(chat.is_crisis),
                crisis_score=chat.crisis_score,
                indicators=indicators
            )

        return ChatResponse(
            id=chat.id,
            session_id=chat.session_id,
            message=chat.message,
            response=chat.response,
            emotion_analysis=emotion_analysis,
            audio_emotion=chat.audio_emotion,
            crisis_detection=crisis_detection,
            created_at=chat.created_at
        )
