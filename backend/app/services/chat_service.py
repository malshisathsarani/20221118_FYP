from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from ..repositories.chat_repo import ChatRepository
from ..ml.unified_pipeline import get_unified_pipeline
from ..ml.rag import get_rag_pipeline
from ..schemas.chat import ChatRequest, ChatResponse, EmotionAnalysis, CrisisDetection
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Service layer for chat-related business logic"""

    def __init__(self, db: Session, use_rag: bool = True):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.ml_pipeline = get_unified_pipeline()
        self.use_rag = use_rag
        if use_rag:
            try:
                self.rag_pipeline = get_rag_pipeline()
                logger.info("RAG pipeline initialized successfully")
            except Exception as e:
                logger.warning(f"RAG pipeline initialization failed: {e}. Continuing without RAG.")
                self.use_rag = False
                self.rag_pipeline = None
        else:
            self.rag_pipeline = None

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

            # Retrieve relevant context using RAG if enabled
            rag_context = None
            rag_sources = []
            if self.use_rag and self.rag_pipeline:
                try:
                    rag_response = self._retrieve_context(
                        message=chat_request.message,
                        crisis_level=crisis_assessment.get('risk_level', 'none'),
                        emotion=fusion_result.get('dominant_emotion', 'neutral')
                    )
                    rag_context = rag_response.get('context')
                    rag_sources = rag_response.get('sources', [])
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}")

            # Generate response based on fusion result and RAG context
            response_text = self._generate_response(
                message=chat_request.message,
                fusion_result=fusion_result,
                crisis_assessment=crisis_assessment,
                rag_context=rag_context
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

    def _retrieve_context(
        self,
        message: str,
        crisis_level: str = 'none',
        emotion: str = 'neutral'
    ) -> Dict:
        """
        Retrieve relevant context from knowledge base using RAG

        Args:
            message: User message
            crisis_level: Crisis risk level
            emotion: Detected emotion

        Returns:
            Dict with context and sources
        """
        # Determine category filter based on crisis level and emotion
        metadata_filter = None
        if crisis_level in ['high', 'critical']:
            metadata_filter = {"category": "crisis"}
        elif emotion in ['sadness', 'fear']:
            # Don't filter, let retriever find most relevant
            pass

        # Retrieve relevant documents
        rag_response = self.rag_pipeline.query(
            query=message,
            top_k=3,
            metadata_filter=metadata_filter,
            max_context_length=1500,
            include_metadata=True,
            use_diversity=True
        )

        # Extract sources
        sources = [
            {
                "doc_id": doc.doc_id,
                "relevance": round(doc.score, 3),
                "category": doc.metadata.get("category", "unknown"),
                "source": doc.metadata.get("source", "unknown")
            }
            for doc in rag_response.retrieved_docs
        ]

        return {
            "context": rag_response.context,
            "sources": sources,
            "num_retrieved": rag_response.metadata["num_retrieved"],
            "avg_score": round(rag_response.metadata["avg_score"], 3)
        }

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

    def _get_response_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get varied response templates for different emotions and risk levels
        Returns a dict with multiple variations to make responses feel more natural
        """
        return {
            'crisis': {
                'opening': [
                    "I can hear that you're going through something really difficult right now, and I want you to know that your feelings are completely valid. ",
                    "It sounds like things feel overwhelming right now. Please know that what you're experiencing matters, and you don't have to face this alone. ",
                    "I'm really glad you felt comfortable sharing this with me. What you're going through sounds incredibly hard, and I want to help. ",
                ],
                'resource': [
                    "There are people who care and want to help - please consider reaching out to a mental health professional or calling the National Suicide Prevention Lifeline at 988. ",
                    "I'd really encourage you to talk to someone who can provide the support you deserve - the National Suicide Prevention Lifeline at 988 is available 24/7. ",
                    "Please reach out to a crisis counselor or call 988 - they're trained to help and are available anytime. ",
                ],
                'closing': [
                    "\n\nWould it help if I shared some immediate support resources with you?",
                    "\n\nI'm here with you. Would you like to talk about what might help right now?",
                    "\n\nYou matter. Can I share some resources that might provide additional support?",
                ]
            },
            'moderate': {
                'sadness': [
                    "I can hear that you're feeling really down right now. It's completely okay to feel this way - these emotions are part of being human. ",
                    "It sounds like you're going through a tough time. Your feelings are valid, and I'm here to listen. ",
                    "That sounds really hard. I want you to know it's okay to not be okay sometimes. ",
                ],
                'fear': [
                    "It sounds like you're feeling anxious about things. Those worries are real, and it makes sense you'd feel this way. ",
                    "I can sense that something's weighing on you. Anxiety can feel so overwhelming, but you're not alone in this. ",
                    "It seems like there's a lot on your mind that's causing you stress. That's totally understandable. ",
                ],
                'anger': [
                    "I hear that you're feeling frustrated or upset. Those are really valid emotions, especially when things feel unfair. ",
                    "It sounds like something's really gotten to you. Anger is a natural response when we feel hurt or wronged. ",
                    "You seem really frustrated right now. That makes sense - sometimes things just get to be too much. ",
                ],
                'neutral': [
                    "I can sense that you're going through something challenging. ",
                    "It sounds like there's something on your mind. ",
                    "I'm picking up that things might not be easy for you right now. ",
                ]
            },
            'low_risk': {
                'sadness': [
                    "I hear you're feeling a bit down. That's okay - we all have those days. ",
                    "It sounds like you're not feeling your best right now. Want to talk about it? ",
                    "I can tell something's bothering you. Sometimes it helps just to share. ",
                ],
                'fear': [
                    "It seems like something's worrying you. Want to talk through it? ",
                    "I can sense a bit of anxiety. What's on your mind? ",
                    "Sounds like you've got some concerns. I'm here to listen. ",
                ],
                'anger': [
                    "I can tell something's frustrated you. That happens to all of us. ",
                    "Sounds like something got under your skin. Want to vent about it? ",
                    "I hear that frustration. Sometimes things just don't go the way we want. ",
                ],
                'joy': [
                    "That's wonderful! I'm so glad to hear you're feeling good! ",
                    "I love that you're feeling positive! That's great! ",
                    "It's so nice to hear some good energy from you! ",
                ],
                'love': [
                    "That's beautiful. It's wonderful when we feel connected and positive. ",
                    "I'm really happy you're experiencing something positive. ",
                    "That sounds lovely. Those feelings are precious. ",
                ],
                'surprise': [
                    "Oh, sounds like something unexpected happened! ",
                    "Life can definitely throw us curveballs sometimes. ",
                    "Well, that's interesting! Unexpected things can be both exciting and unsettling. ",
                ],
                'neutral': [
                    "I'm here and listening. What's on your mind today? ",
                    "Thanks for sharing with me. How are things going? ",
                    "I'm glad you're here. What would you like to talk about? ",
                ]
            },
            'follow_up': [
                "What else is going on?",
                "Tell me more about that.",
                "How has this been affecting you?",
                "What's been the hardest part?",
                "Is there anything specific that's been on your mind?",
                "How are you coping with all this?",
                "What would help you feel better right now?",
            ]
        }

    def _generate_response(
        self,
        message: str,
        fusion_result: Dict,
        crisis_assessment: Dict,
        rag_context: Optional[str] = None
    ) -> str:
        """
        Generate appropriate response based on fusion analysis and RAG context

        Uses multi-modal fusion result and retrieved knowledge to create
        empathetic, evidence-based, context-aware response
        """
        import random

        risk_level = fusion_result.get('overall_risk_level', 'none')
        dominant_emotion = fusion_result.get('dominant_emotion', 'neutral')
        emotional_state = fusion_result.get('emotional_state', 'stable')

        # Get response templates
        templates = self._get_response_templates()

        # Critical/High risk responses (RAG-enhanced with crisis protocols)
        if risk_level in ['critical', 'high']:
            # Use varied, warm opening instead of scripted response
            base_response = random.choice(templates['crisis']['opening'])

            # Add crisis resources in a natural way
            base_response += random.choice(templates['crisis']['resource'])

            # Blend RAG context naturally if available
            if rag_context:
                crisis_support = self._extract_crisis_support(rag_context)
                if crisis_support:
                    # Make it sound conversational, not copy-pasted
                    base_response += f"\n\n{crisis_support} "

            # Warm, caring closing
            base_response += random.choice(templates['crisis']['closing'])

            return base_response

        # Moderate risk responses (RAG-enhanced with coping strategies)
        if risk_level == 'moderate':
            # Get emotion-specific template
            emotion_templates = templates['moderate'].get(dominant_emotion, templates['moderate']['neutral'])
            base_response = random.choice(emotion_templates)

            # Add varied follow-up question
            follow_ups = [
                "Would you like to talk more about what's been going on? ",
                "Do you want to share more about what's troubling you? ",
                "I'm here if you want to talk through this. ",
            ]
            response = base_response + random.choice(follow_ups)

            # Blend RAG coping strategies naturally
            if rag_context:
                coping_info = self._extract_coping_strategies(rag_context)
                if coping_info:
                    response += f"\n\n{coping_info}\n\n"

            # Gentle support reminder with variation
            support_reminders = [
                "I'm here to listen and support you. If things start feeling overwhelming, reaching out to a counselor could really help.",
                "Remember, I'm here for you. And if you ever need more support, talking to a therapist can make a real difference.",
                "You don't have to handle this alone. I'm here, and professional support is always available if you need it.",
            ]
            response += random.choice(support_reminders)

            return response

        # Low risk / Normal conversation (RAG-enhanced with helpful information)
        # Get emotion-specific template from low_risk category
        emotion_templates = templates['low_risk'].get(dominant_emotion, templates['low_risk']['neutral'])
        base_response = random.choice(emotion_templates)

        # Add RAG context naturally if available
        if rag_context:
            context_snippet = self._extract_relevant_snippet(rag_context, max_length=200)
            if context_snippet:
                # Blend context and add varied follow-up
                response = f"{base_response}\n\n{context_snippet}\n\n{random.choice(templates['follow_up'])}"
                return response

        # Without RAG context, add natural follow-up question
        return f"{base_response} {random.choice(templates['follow_up'])}"

    def _extract_crisis_support(self, context: str, max_length: int = 300) -> str:
        """Extract crisis-relevant information from RAG context"""
        # Simple extraction - look for crisis-related keywords
        lines = context.split('\n')
        relevant_lines = []

        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in [
                'crisis', 'suicide', 'emergency', 'immediate', 'call', 'hotline'
            ]):
                relevant_lines.append(line)

        result = ' '.join(relevant_lines)[:max_length]
        return result if result else ""

    def _extract_coping_strategies(self, context: str, max_length: int = 250) -> str:
        """Extract coping strategies from RAG context in a conversational way"""
        import random

        lines = context.split('\n')
        relevant_lines = []

        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in [
                'technique', 'strategy', 'practice', 'exercise', 'breathing',
                'mindfulness', 'coping', 'help', 'manage'
            ]):
                relevant_lines.append(line)

        result = ' '.join(relevant_lines)[:max_length]
        if result:
            # Make it sound conversational, not like citing research
            intro_phrases = [
                "Something that might help: ",
                "Here's an idea that could be useful: ",
                "You might want to try this: ",
                "One thing that often helps people: ",
                "A technique worth considering: ",
            ]
            return random.choice(intro_phrases) + result
        return ""

    def _extract_relevant_snippet(self, context: str, max_length: int = 300) -> str:
        """Extract a relevant snippet from RAG context in a natural way"""
        if not context:
            return ""

        # Remove metadata headers like [Source: ...] and separators
        import re
        import random

        clean_context = re.sub(r'\[Source:.*?\]', '', context)
        clean_context = clean_context.replace('---', '').strip()

        # Split into sentences and take the most relevant ones
        sentences = [s.strip() for s in clean_context.split('.') if s.strip() and len(s.strip()) > 20]

        if not sentences:
            return ""

        # Build snippet from sentences
        snippet = ""
        for sentence in sentences[:3]:  # Take up to 3 sentences
            if len(snippet) + len(sentence) < max_length:
                snippet += sentence + ". "
            else:
                break

        snippet = snippet.strip()

        # Make it conversational - avoid sounding like you're citing a textbook
        if snippet:
            # More natural intro phrases
            intro_phrases = [
                "Something that comes to mind: ",
                "Here's a thought: ",
                "You know, ",
                "From what I understand, ",
                "One thing to consider: ",
                "This might be helpful: ",
            ]
            return random.choice(intro_phrases) + snippet

        return ""

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
