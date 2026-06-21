from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Any
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

        logger.info(f"ChatService initializing with use_rag={use_rag}")

        if use_rag:
            try:
                logger.info("Attempting to initialize RAG pipeline...")
                self.rag_pipeline = get_rag_pipeline()
                logger.info("✓ RAG pipeline initialized successfully in ChatService")
            except Exception as e:
                logger.error(f"✗ RAG pipeline initialization failed: {e}", exc_info=True)
                logger.warning("Continuing without RAG due to initialization failure")
                self.use_rag = False
                self.rag_pipeline = None
        else:
            logger.info("RAG disabled by configuration")
            self.rag_pipeline = None

    def process_message(self, user_id: int, chat_request: ChatRequest) -> ChatResponse:
        """Process a chat message with comprehensive ML analysis using unified pipeline"""
        temp_audio_path = None
        try:
            # Download audio from URL if provided
            audio_path = None
            if chat_request.audio_data:
                from ..ml.shared.audio_utils import download_audio_from_url
                temp_audio_path = download_audio_from_url(chat_request.audio_data)
                if temp_audio_path:
                    audio_path = temp_audio_path
                    logger.info(f"Audio downloaded for processing: {audio_path}")
                else:
                    logger.warning("Failed to download audio, continuing with text-only analysis")

            # Run comprehensive analysis through unified pipeline
            analysis = self.ml_pipeline.analyze_comprehensive(
                text=chat_request.message,
                audio_path=audio_path  # Local file path for ML processing
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

            # Generate response based on fusion result, RAG context, and session history
            response_text = self._generate_response(
                message=chat_request.message,
                fusion_result=fusion_result,
                crisis_assessment=crisis_assessment,
                rag_context=rag_context,
                session_id=chat_request.session_id  # Pass session_id for history
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
        finally:
            # Cleanup temporary audio file
            if temp_audio_path:
                from ..ml.shared.audio_utils import cleanup_temp_audio
                cleanup_temp_audio(temp_audio_path)

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

    def _analyze_session_history(self, session_id: str, limit: int = 5) -> Dict[str, Any]:
        """
        Analyze recent session history to understand conversation context

        Returns:
            Dict with session patterns, recurring topics, emotional progression
        """
        # Get recent messages from this session
        recent_chats = self.chat_repo.get_by_session(session_id, limit=limit)

        if not recent_chats or len(recent_chats) == 0:
            return {
                'has_history': False,
                'message_count': 0,
                'recurring_topics': [],
                'recent_emotions': [],
                'emotion_trend': 'stable',
                'recent_messages': []
            }

        # Extract patterns
        emotions = [chat.detected_emotion for chat in recent_chats if chat.detected_emotion]
        crisis_levels = [chat.is_crisis for chat in recent_chats]
        recent_messages = [chat.message for chat in recent_chats]

        # Identify recurring topics from recent messages
        all_topics = []
        for msg in recent_messages:
            msg_analysis = self._analyze_message(msg)
            all_topics.extend(msg_analysis.get('topics', []))

        # Count topic frequency
        from collections import Counter
        topic_counts = Counter(all_topics)
        recurring_topics = [topic for topic, count in topic_counts.items() if count >= 2]

        # Determine emotional trend
        emotion_trend = 'stable'
        if len(emotions) >= 3:
            negative_emotions = ['sadness', 'fear', 'anger']
            recent_negative = sum(1 for e in emotions[-3:] if e in negative_emotions)
            older_negative = sum(1 for e in emotions[:-3] if e in negative_emotions) if len(emotions) > 3 else 0

            if recent_negative > older_negative:
                emotion_trend = 'worsening'
            elif recent_negative < older_negative:
                emotion_trend = 'improving'

        # Check for crisis escalation
        crisis_escalating = False
        if len(crisis_levels) >= 2:
            crisis_escalating = crisis_levels[-1] > crisis_levels[-2]

        return {
            'has_history': True,
            'message_count': len(recent_chats),
            'recurring_topics': recurring_topics,
            'recent_emotions': emotions[-3:] if len(emotions) >= 3 else emotions,
            'emotion_trend': emotion_trend,
            'crisis_escalating': crisis_escalating,
            'recent_messages': recent_messages[-2:],  # Last 2 messages for reference
            'dominant_recent_emotion': emotions[-1] if emotions else None
        }

    def _detect_emotion_intensity(self, message: str, emotion_confidence: float) -> str:
        """
        Detect intensity of emotion from message text and confidence
        Returns: 'mild', 'moderate', 'intense'
        """
        message_lower = message.lower()

        # Intensity indicators
        intense_indicators = [
            'extremely', 'completely', 'totally', 'absolutely', 'unbearably',
            'can\'t take', 'so much', 'too much', 'overwhelming', 'crushing',
            'destroying', 'killing me', 'can\'t handle', 'breaking down',
            'can\'t go on', 'give up', 'hopeless', 'desperate'
        ]

        moderate_indicators = [
            'very', 'really', 'quite', 'pretty', 'significantly',
            'struggling', 'difficult', 'hard time', 'tough', 'challenging'
        ]

        mild_indicators = [
            'a bit', 'a little', 'kind of', 'sort of', 'somewhat',
            'slightly', 'not great', 'not the best', 'okay', 'fine'
        ]

        # Check for intensity markers in message
        if any(indicator in message_lower for indicator in intense_indicators):
            return 'intense'
        elif any(indicator in message_lower for indicator in moderate_indicators):
            return 'moderate'
        elif any(indicator in message_lower for indicator in mild_indicators):
            return 'mild'

        # Fall back to confidence score
        if emotion_confidence > 0.75:
            return 'intense'
        elif emotion_confidence > 0.5:
            return 'moderate'
        else:
            return 'mild'

    def _analyze_message(self, message: str) -> Dict[str, Any]:
        """
        Analyze user message to extract key information for personalization

        Returns:
            Dict with message analysis including topics, key phrases, question type
        """
        import re

        message_lower = message.lower()

        # Detect if it's a question
        is_question = '?' in message or any(message_lower.startswith(q) for q in [
            'how', 'what', 'why', 'when', 'where', 'who', 'can', 'could',
            'should', 'would', 'is', 'are', 'do', 'does'
        ])

        # Extract key emotional/mental health topics
        topics = []
        topic_keywords = {
            'work_stress': ['work', 'job', 'boss', 'career', 'office', 'colleague'],
            'relationship': ['relationship', 'partner', 'boyfriend', 'girlfriend', 'spouse', 'marriage', 'breakup', 'divorce'],
            'family': ['family', 'parent', 'mother', 'father', 'mom', 'dad', 'sibling', 'brother', 'sister'],
            'loneliness': ['lonely', 'alone', 'isolated', 'nobody', 'no one'],
            'anxiety': ['anxious', 'worried', 'nervous', 'panic', 'overwhelmed'],
            'depression': ['depressed', 'hopeless', 'worthless', 'empty', 'numb'],  # Removed 'sad' - it's too general
            'self_harm': ['hurt myself', 'harm', 'cut', 'suicide', 'kill myself', 'end it', 'die'],
            'sleep': ['sleep', 'insomnia', 'tired', 'exhausted', 'can\'t sleep'],
            'health': ['sick', 'pain', 'ill', 'disease', 'diagnosis'],
            'financial': ['money', 'debt', 'financial', 'bills', 'broke', 'afford'],
            'school': ['school', 'college', 'university', 'exam', 'grades', 'study']
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)

        # Extract important phrases (noun phrases, concerns)
        # Simple extraction: look for phrases after "about", "with", "because"
        concern_phrases = []
        concern_patterns = [
            r'(?:about|regarding|concerning)\s+([^.,!?]+)',
            r'(?:with|from)\s+(my|the|this)\s+([^.,!?]+)',
            r'because\s+([^.,!?]+)',
        ]

        for pattern in concern_patterns:
            matches = re.findall(pattern, message_lower)
            for match in matches:
                if isinstance(match, tuple):
                    phrase = ' '.join(match).strip()
                else:
                    phrase = match.strip()
                if len(phrase) > 3 and len(phrase) < 50:  # Reasonable length
                    concern_phrases.append(phrase)

        # Detect sentiment indicators
        negative_words = sum(1 for word in ['not', 'no', 'never', 'nothing', 'nobody', 'can\'t', 'won\'t', 'don\'t'] if word in message_lower.split())

        # Extract key verbs (what they're doing/feeling)
        feeling_verbs = []
        feeling_patterns = [
            r'i(?:\'m| am)\s+(feeling|felt|feel)\s+([^.,!?]+)',
            r'i(?:\'m| am)\s+([^.,!?]{3,20})',  # "I'm overwhelmed", "I'm struggling"
        ]

        for pattern in feeling_patterns:
            matches = re.findall(pattern, message_lower)
            for match in matches:
                if isinstance(match, tuple):
                    verb = match[-1].strip()
                else:
                    verb = match.strip()
                if verb and len(verb) > 2:
                    feeling_verbs.append(verb)

        return {
            'is_question': is_question,
            'topics': topics,
            'concern_phrases': concern_phrases[:3],  # Top 3
            'feeling_verbs': feeling_verbs[:2],  # Top 2
            'message_length': len(message.split()),
            'has_negation': negative_words > 0,
            'urgency': len([w for w in ['urgent', 'emergency', 'immediate', 'now', 'help'] if w in message_lower])
        }

    def _build_conversation_context(
        self,
        session_history: Dict[str, Any],
        current_message_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build conversation context by combining session history with current message

        Returns:
            Dict with context flags for response generation
        """
        import random

        context = {
            'is_continuation': False,
            'topic_mentioned_before': False,
            'emotion_changing': False,
            'should_acknowledge_progress': False,
            'continuity_phrase': None,
            'recurring_topic': None
        }

        if not session_history.get('has_history'):
            return context

        # Check if current topics were mentioned before
        current_topics = current_message_analysis.get('topics', [])
        recurring_topics = session_history.get('recurring_topics', [])

        for topic in current_topics:
            if topic in recurring_topics:
                context['is_continuation'] = True
                context['topic_mentioned_before'] = True
                context['recurring_topic'] = topic
                break

        # Check emotional progression
        current_emotion = current_message_analysis.get('topics', [])
        if 'anxiety' in current_emotion or 'depression' in current_emotion:
            emotion_trend = session_history.get('emotion_trend')
            if emotion_trend == 'improving':
                context['should_acknowledge_progress'] = True
            elif emotion_trend == 'worsening':
                context['emotion_changing'] = True

        # Generate continuity phrases based on context
        if context['topic_mentioned_before']:
            topic_name_map = {
                'work_stress': 'work',
                'relationship': 'your relationship',
                'family': 'your family situation',
                'loneliness': 'feeling isolated',
                'anxiety': 'the anxiety',
                'sleep': 'sleep troubles',
                'financial': 'money concerns',
                'school': 'school stress'
            }
            topic_display = topic_name_map.get(context['recurring_topic'], 'this')

            continuity_phrases = [
                f"I remember you mentioned {topic_display} earlier. ",
                f"You've brought up {topic_display} before. ",
                f"It sounds like {topic_display} is still on your mind. ",
                f"{topic_display.capitalize()} is still weighing on you. ",
            ]
            context['continuity_phrase'] = random.choice(continuity_phrases)

        return context

    def _create_personalized_acknowledgment(self, message_analysis: Dict[str, Any]) -> str:
        """
        Create a personalized acknowledgment based on message analysis
        Makes the bot reference specific things the user mentioned
        """
        import random

        topics = message_analysis.get('topics', [])
        concern_phrases = message_analysis.get('concern_phrases', [])
        feeling_verbs = message_analysis.get('feeling_verbs', [])
        is_question = message_analysis.get('is_question', False)

        # Topic-specific acknowledgments
        topic_acknowledgments = {
            'work_stress': ["Work stress can be really tough to handle. ", "I hear that work has been weighing on you. ", "Job pressures can feel overwhelming. "],
            'relationship': ["Relationship struggles are never easy. ", "I can tell this relationship situation is affecting you. ", "Matters of the heart can be so challenging. "],
            'family': ["Family dynamics can be complicated. ", "I hear that family issues are on your mind. ", "Family situations can feel really heavy. "],
            'loneliness': ["Feeling isolated is really hard. ", "Loneliness can be such a painful experience. ", "I hear that you're feeling alone right now. "],
            'anxiety': ["Anxiety can feel so overwhelming. ", "I can sense the worry you're carrying. ", "That anxious feeling is really difficult. "],
            'depression': ["Depression makes everything feel harder. ", "I can hear how heavy things feel for you. ", "What you're describing sounds really difficult. "],
            'sleep': ["Sleep issues can affect everything else. ", "Not sleeping well makes everything harder. ", "I hear that sleep has been difficult. "],
            'financial': ["Money worries create so much stress. ", "Financial pressure is really tough. ", "I understand money concerns are weighing on you. "],
            'school': ["Academic pressure can feel intense. ", "School stress is really challenging. ", "I hear that your studies are weighing on you. "],
        }

        acknowledgment = ""

        # Use topic-specific acknowledgment if available
        if topics:
            primary_topic = topics[0]
            if primary_topic in topic_acknowledgments:
                acknowledgment = random.choice(topic_acknowledgments[primary_topic])

        # Add specific concern if mentioned
        if concern_phrases and concern_phrases[0]:
            concern = concern_phrases[0]
            acknowledgment += f"What you mentioned about {concern} sounds really challenging. "

        # Reference their feeling if they expressed it
        if feeling_verbs and feeling_verbs[0]:
            feeling = feeling_verbs[0]
            if not acknowledgment:  # Only if we haven't acknowledged yet
                acknowledgment = f"I hear that you're {feeling}. "

        return acknowledgment

    def _get_progress_acknowledgment(self, emotion_trend: str) -> Optional[str]:
        """
        Acknowledge emotional progress if user is improving
        Makes conversation feel continuous and supportive
        """
        import random

        if emotion_trend == 'improving':
            acknowledgments = [
                "I'm glad to hear things seem a bit better than last time we talked. ",
                "It sounds like you're feeling a little more positive than earlier. ",
                "I can sense some improvement from our earlier conversation. ",
                "There seems to be a bit of a shift from how you were feeling before. ",
            ]
            return random.choice(acknowledgments)
        elif emotion_trend == 'worsening':
            acknowledgments = [
                "I notice things seem harder than when we last talked. ",
                "It sounds like things have gotten more difficult since earlier. ",
                "I can hear that you're struggling more than before. ",
            ]
            return random.choice(acknowledgments)

        return None

    def _get_natural_filler(self, context: str = 'opening') -> str:
        """
        Get natural filler phrases to make responses sound more human
        Context: 'opening', 'transition', 'empathy', 'agreement'
        """
        import random

        fillers = {
            'opening': [
                "You know, ",
                "I hear you - ",
                "Honestly, ",
                "I can really sense that ",
                "",  # Sometimes no filler is more natural
                ""
            ],
            'transition': [
                "And you know what? ",
                "Here's the thing - ",
                "I think ",
                "What I'm hearing is that ",
                "From what you're sharing, ",
                ""
            ],
            'empathy': [
                "I really hear you. ",
                "That makes total sense. ",
                "I can understand why you'd feel that way. ",
                "That's completely valid. ",
                ""
            ],
            'agreement': [
                "Absolutely. ",
                "Yeah, ",
                "I get that. ",
                "For sure. ",
                "That's real. ",
                ""
            ]
        }

        return random.choice(fillers.get(context, ['']))

    def _create_reflective_response(self, message: str, emotion: str) -> Optional[str]:
        """
        Create a reflective listening response that mirrors back what user said
        This validates their experience and shows active listening
        """
        import random
        import re

        message_lower = message.lower()

        # Extract key phrases to reflect back
        reflection_patterns = [
            (r"i (?:feel|felt|am feeling) ([^.,!?]+)", "So you're feeling {}, "),
            (r"(?:can't|cannot) ([^.,!?]+)", "It sounds like you can't {}, "),
            (r"(?:struggling|struggle) with ([^.,!?]+)", "You're struggling with {}, "),
            (r"i'm ([^.,!?]+)", "So you're {}, "),
        ]

        for pattern, template in reflection_patterns:
            match = re.search(pattern, message_lower)
            if match:
                reflected = match.group(1).strip()
                if len(reflected) > 3 and len(reflected) < 40:
                    return template.format(reflected)

        # Generic reflections based on emotion
        emotion_reflections = {
            'sadness': [
                "It sounds like you're going through a really tough time. ",
                "I hear that things are feeling heavy right now. "
            ],
            'fear': [
                "It sounds like there's a lot weighing on your mind. ",
                "I hear that you're dealing with some difficult worries. "
            ],
            'anger': [
                "It sounds like something's really gotten to you. ",
                "I hear that you're dealing with some frustrating situations. "
            ]
        }

        if emotion in emotion_reflections:
            return random.choice(emotion_reflections[emotion])

        return None

    def _get_topic_specific_followup(self, topics: List[str]) -> Optional[str]:
        """
        Get topic-specific follow-up questions or comments
        Makes conversation feel tailored to their situation
        """
        import random

        if not topics:
            return None

        topic_followups = {
            'work_stress': [
                "How long has this been going on at work?",
                "Is there something specific at work that's been triggering this?",
                "Have you been able to talk to anyone about what's happening at work?",
            ],
            'relationship': [
                "How has this been affecting you day-to-day?",
                "Have you two been able to talk about this?",
                "How long have you been feeling this way about the relationship?",
            ],
            'family': [
                "How has this family situation been impacting you?",
                "Is this a new issue or something that's been ongoing?",
                "Have you had anyone to talk to about this?",
            ],
            'loneliness': [
                "How long have you been feeling this way?",
                "Is there anyone in your life you feel you can reach out to?",
                "What usually helps when you're feeling isolated?",
            ],
            'sleep': [
                "How long has sleep been an issue?",
                "Have you noticed what might be affecting your sleep?",
                "How is the lack of sleep impacting your daily life?",
            ],
            'financial': [
                "How long have you been dealing with this financial stress?",
                "Is there anyone who can help you think through options?",
                "How is this affecting your day-to-day life?",
            ],
            'school': [
                "How are you managing with everything on your plate?",
                "Is there a particular aspect of school that's most stressful?",
                "Have you been able to talk to anyone about the academic pressure?",
            ],
        }

        primary_topic = topics[0]
        if primary_topic in topic_followups:
            return random.choice(topic_followups[primary_topic])

        return None

    def _get_intensity_response(self, emotion: str, intensity: str) -> Optional[str]:
        """
        Get emotion and intensity-aware opening responses
        Provides nuanced responses based on how intense the emotion is
        """
        import random

        intensity_responses = {
            'sadness': {
                'mild': [
                    "I can tell something's weighing on you a bit. ",
                    "It sounds like you're not feeling your best today. ",
                    "I hear you're going through a rough patch. "
                ],
                'moderate': [
                    "I can hear that you're feeling pretty down right now. ",
                    "It sounds like things have been tough lately. ",
                    "I can sense you're dealing with some real sadness. "
                ],
                'intense': [
                    "I can hear that you're in a lot of pain right now. ",
                    "It sounds like you're really struggling with how you're feeling. ",
                    "I can tell you're going through something extremely difficult. "
                ]
            },
            'fear': {
                'mild': [
                    "It seems like something's on your mind. ",
                    "I can sense a bit of worry there. ",
                    "Sounds like you've got some concerns. "
                ],
                'moderate': [
                    "I can hear that you're feeling pretty anxious about this. ",
                    "It sounds like this is causing you real stress. ",
                    "I can sense you're dealing with some significant worry. "
                ],
                'intense': [
                    "I can hear that the anxiety is really overwhelming right now. ",
                    "It sounds like you're dealing with a lot of fear and stress. ",
                    "I can tell this is causing you intense worry. "
                ]
            },
            'anger': {
                'mild': [
                    "I can tell something's bothering you. ",
                    "Sounds like something got to you a bit. ",
                    "I hear a bit of frustration there. "
                ],
                'moderate': [
                    "I can hear that you're feeling pretty frustrated with this. ",
                    "It sounds like something's really getting under your skin. ",
                    "I can sense some real anger there - that's valid. "
                ],
                'intense': [
                    "I can hear how angry and frustrated you are - those feelings are real. ",
                    "It sounds like you're dealing with a lot of rage right now. ",
                    "I can tell this has pushed you to your limit. "
                ]
            }
        }

        if emotion in intensity_responses and intensity in intensity_responses[emotion]:
            return random.choice(intensity_responses[emotion][intensity])

        return None

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
        rag_context: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Generate appropriate response based on fusion analysis, RAG context, and session history

        Uses multi-modal fusion result, retrieved knowledge, and conversation history to create
        empathetic, evidence-based, context-aware response
        """
        import random

        risk_level = fusion_result.get('overall_risk_level', 'none')
        dominant_emotion = fusion_result.get('dominant_emotion', 'neutral')
        emotional_state = fusion_result.get('emotional_state', 'stable')
        emotion_confidence = fusion_result.get('dominant_emotion_confidence', 0.5)

        # Detect emotion intensity for nuanced responses
        intensity = self._detect_emotion_intensity(message, emotion_confidence)

        # Analyze message for personalization
        message_analysis = self._analyze_message(message)

        # Analyze session history for conversation continuity
        session_history = {'has_history': False}
        conversation_context = None
        if session_id:
            session_history = self._analyze_session_history(session_id)
            conversation_context = self._build_conversation_context(session_history, message_analysis)

        # Get response templates
        templates = self._get_response_templates()

        # Critical/High risk responses (RAG-enhanced with crisis protocols)
        if risk_level in ['critical', 'high']:
            base_response = ""

            # Add continuity phrase if topic mentioned before
            if conversation_context and conversation_context.get('continuity_phrase'):
                base_response = conversation_context['continuity_phrase']

            # Add personalized acknowledgment if available
            personalized_ack = self._create_personalized_acknowledgment(message_analysis)
            if personalized_ack:
                base_response += personalized_ack

            # Add crisis opening
            base_response += random.choice(templates['crisis']['opening'])

            # Acknowledge if situation is worsening
            if conversation_context and conversation_context.get('emotion_changing'):
                base_response += "I'm especially concerned that things seem to be getting harder for you. "

            # Add crisis resources in a natural way
            base_response += random.choice(templates['crisis']['resource'])

            # Blend RAG context naturally if available
            if rag_context:
                crisis_support = self._extract_crisis_support(rag_context)
                if crisis_support:
                    # Format for crisis context
                    formatted_support = self._format_rag_for_context(crisis_support, risk_level, dominant_emotion)
                    base_response += f"\n\n{formatted_support} "

            # Warm, caring closing
            base_response += random.choice(templates['crisis']['closing'])

            return base_response

        # Moderate risk responses (RAG-enhanced with coping strategies)
        if risk_level == 'moderate':
            response = ""

            # Add natural opening filler sometimes
            opening_filler = self._get_natural_filler('opening')
            if opening_filler:
                response += opening_filler

            # Add continuity phrase if topic mentioned before
            if conversation_context and conversation_context.get('continuity_phrase'):
                response += conversation_context['continuity_phrase']

            # Acknowledge emotional progress if applicable
            if session_history.get('has_history'):
                progress_ack = self._get_progress_acknowledgment(session_history.get('emotion_trend', 'stable'))
                if progress_ack:
                    response += progress_ack

            # Try reflective listening first for natural feel
            reflective = self._create_reflective_response(message, dominant_emotion)
            if reflective:
                response += reflective

            # Add intensity-aware response
            intensity_response = self._get_intensity_response(dominant_emotion, intensity)
            if intensity_response:
                response += intensity_response
            else:
                # Add personalized acknowledgment if available
                personalized_ack = self._create_personalized_acknowledgment(message_analysis)
                if personalized_ack:
                    response += personalized_ack
                else:
                    # Get emotion-specific template
                    emotion_templates = templates['moderate'].get(dominant_emotion, templates['moderate']['neutral'])
                    response += random.choice(emotion_templates)

            # Add empathy filler
            response += self._get_natural_filler('empathy')

            # Add topic-specific follow-up if available
            topic_followup = self._get_topic_specific_followup(message_analysis.get('topics', []))
            if topic_followup:
                response += topic_followup + " "
            else:
                # Add varied follow-up question
                follow_ups = [
                    "Would you like to talk more about what's been going on? ",
                    "Do you want to share more about what's troubling you? ",
                    "I'm here if you want to talk through this. ",
                ]
                response += random.choice(follow_ups)

            # Blend RAG coping strategies naturally
            if rag_context:
                coping_info = self._extract_coping_strategies(rag_context)
                if coping_info:
                    # Format for moderate-risk context
                    formatted_info = self._format_rag_for_context(coping_info, risk_level, dominant_emotion)
                    # Add smooth transition
                    smooth_info = self._create_smooth_transition(response, formatted_info, risk_level)
                    response += f"\n\n{smooth_info}\n\n"

            # Gentle support reminder with variation
            support_reminders = [
                "I'm here to listen and support you. If things start feeling overwhelming, reaching out to a counselor could really help.",
                "Remember, I'm here for you. And if you ever need more support, talking to a therapist can make a real difference.",
                "You don't have to handle this alone. I'm here, and professional support is always available if you need it.",
            ]
            response += random.choice(support_reminders)

            return response

        # Low risk / Normal conversation (RAG-enhanced with helpful information)
        base_response = ""

        # Add natural opening filler for casual tone
        opening_filler = self._get_natural_filler('opening')
        if opening_filler:
            base_response += opening_filler

        # Add continuity phrase if topic mentioned before
        if conversation_context and conversation_context.get('continuity_phrase'):
            base_response += conversation_context['continuity_phrase']

        # Acknowledge emotional progress if user is improving
        if session_history.get('has_history'):
            progress_ack = self._get_progress_acknowledgment(session_history.get('emotion_trend', 'stable'))
            if progress_ack:
                base_response += progress_ack
                # Add agreement filler after progress acknowledgment
                base_response += self._get_natural_filler('agreement')

        # Try reflective listening for more natural feel
        reflective = self._create_reflective_response(message, dominant_emotion)
        if reflective:
            base_response += reflective

        # Add intensity-aware response for nuanced understanding
        intensity_response = self._get_intensity_response(dominant_emotion, intensity)
        if intensity_response:
            base_response += intensity_response
        else:
            # Add personalized acknowledgment if available
            personalized_ack = self._create_personalized_acknowledgment(message_analysis)
            if personalized_ack:
                base_response += personalized_ack
            else:
                # Get emotion-specific template from low_risk category
                emotion_templates = templates['low_risk'].get(dominant_emotion, templates['low_risk']['neutral'])
                base_response += random.choice(emotion_templates)

        # Use topic-specific follow-up if available
        topic_followup = self._get_topic_specific_followup(message_analysis.get('topics', []))

        # Add RAG context naturally if available
        if rag_context:
            context_snippet = self._extract_relevant_snippet(rag_context, max_length=200)
            if context_snippet:
                # Format for low-risk context
                formatted_snippet = self._format_rag_for_context(context_snippet, risk_level, dominant_emotion)
                # Add smooth transition
                smooth_snippet = self._create_smooth_transition(base_response, formatted_snippet, risk_level)

                # Blend context and add personalized follow-up
                if topic_followup:
                    response = f"{base_response}\n\n{smooth_snippet}\n\n{topic_followup}"
                else:
                    response = f"{base_response}\n\n{smooth_snippet}\n\n{random.choice(templates['follow_up'])}"
                return response

        # Without RAG context, use topic-specific or general follow-up
        if topic_followup:
            return f"{base_response} {topic_followup}"
        else:
            return f"{base_response} {random.choice(templates['follow_up'])}"

    def _clean_rag_text(self, text: str) -> str:
        """
        Clean RAG text by removing metadata, markers, and formatting issues
        Makes text more natural and conversational
        """
        import re

        # Remove common metadata markers
        text = re.sub(r'\[Source:.*?\]', '', text)
        text = re.sub(r'\[Document ID:.*?\]', '', text)
        text = re.sub(r'\[Page \d+\]', '', text)
        text = re.sub(r'Document \d+:', '', text)

        # Remove separators
        text = text.replace('---', '')
        text = text.replace('===', '')
        text = text.replace('***', '')

        # Remove bullet points and list markers
        text = re.sub(r'^\s*[\-\*\•]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Remove citation markers like [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)

        return text

    def _extract_crisis_support(self, context: str, max_length: int = 300) -> str:
        """Extract crisis-relevant information from RAG context in a supportive way"""
        import re
        import random

        # Clean the context first
        clean_context = self._clean_rag_text(context)

        lines = clean_context.split('.')
        relevant_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for crisis-related content
            if any(keyword in line.lower() for keyword in [
                'crisis', 'suicide', 'emergency', 'immediate', 'call', 'hotline',
                'help', 'support', 'resource', 'available', '988', 'lifeline'
            ]):
                # Skip overly technical or impersonal lines
                if not any(skip in line.lower() for skip in ['study', 'research shows', 'data', 'statistics']):
                    relevant_lines.append(line)

        if not relevant_lines:
            return ""

        # Build result focusing on actionable, supportive information
        result = '. '.join(relevant_lines[:2])[:max_length]  # Max 2 sentences

        if result:
            # Make it sound supportive, not clinical
            supportive_intros = [
                "There are immediate resources that can help: ",
                "Help is available right now: ",
                "You can get support immediately: ",
            ]
            return random.choice(supportive_intros) + result + "."

        return ""

    def _simplify_text(self, text: str) -> str:
        """
        Simplify complex/academic text to make it more conversational
        """
        # Replace formal phrases with casual ones
        replacements = {
            'individuals': 'people',
            'utilize': 'use',
            'implement': 'try',
            'demonstrates': 'shows',
            'indicates': 'suggests',
            'furthermore': 'also',
            'therefore': 'so',
            'however': 'but',
            'nevertheless': 'still',
            'subsequently': 'then',
            'approximately': 'about',
            'numerous': 'many',
            'sufficient': 'enough',
            'commence': 'start',
            'terminate': 'end',
        }

        text_lower = text
        for formal, casual in replacements.items():
            # Case-insensitive replacement
            import re
            text_lower = re.sub(r'\b' + formal + r'\b', casual, text_lower, flags=re.IGNORECASE)

        return text_lower

    def _extract_coping_strategies(self, context: str, max_length: int = 250) -> str:
        """Extract coping strategies from RAG context in a conversational way"""
        import random
        import re

        # Clean the context first
        clean_context = self._clean_rag_text(context)

        lines = clean_context.split('.')
        relevant_lines = []

        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue

            # Look for strategy-related content
            if any(keyword in line.lower() for keyword in [
                'technique', 'strategy', 'practice', 'exercise', 'breathing',
                'mindfulness', 'coping', 'can help', 'try', 'manage', 'reduce',
                'relax', 'calm', 'focus', 'ground'
            ]):
                # Skip overly technical or research-focused lines
                if not any(skip in line.lower() for skip in [
                    'study', 'research', 'p <', 'statistical', 'hypothesis',
                    'correlation', 'participants', 'meta-analysis'
                ]):
                    relevant_lines.append(line)

        if not relevant_lines:
            return ""

        # Take best 1-2 sentences
        result = '. '.join(relevant_lines[:2])[:max_length]

        # Simplify the text
        result = self._simplify_text(result)

        # Make sure it ends with a period
        if result and not result.endswith('.'):
            result += '.'

        if result:
            # Make it sound like sharing helpful advice, not quoting a textbook
            intro_phrases = [
                "Something that might help: ",
                "Here's an idea - ",
                "You could try this: ",
                "One thing that often helps: ",
                "A technique worth trying: ",
                "What sometimes works: ",
            ]
            return random.choice(intro_phrases) + result
        return ""

    def _create_smooth_transition(
        self,
        from_text: str,
        to_rag_content: str,
        risk_level: str
    ) -> str:
        """
        Create smooth transition between empathetic response and RAG content
        Makes the flow feel natural, not jarring
        """
        import random

        if not to_rag_content:
            return ""

        # For crisis, transition is direct (urgent info)
        if risk_level in ['critical', 'high']:
            return to_rag_content

        # For moderate/low, add a subtle connector if needed
        # Check if RAG content already has a natural intro
        has_intro = any(intro in to_rag_content.lower()[:30] for intro in [
            'something', 'here', 'you', 'one thing', 'what', 'this might', 'i'
        ])

        if has_intro:
            # Already has good intro, just return it
            return to_rag_content

        # Add a subtle connector
        connectors = [
            "By the way, ",
            "Also, ",
            "Just so you know, ",
            "",  # Sometimes no connector is best
        ]

        return random.choice(connectors) + to_rag_content

    def _format_rag_for_context(
        self,
        rag_content: str,
        risk_level: str,
        dominant_emotion: str,
        topic: Optional[str] = None
    ) -> str:
        """
        Format RAG content based on conversation context
        Different formatting for crisis vs. general conversation
        """
        import random

        if not rag_content:
            return ""

        # For crisis situations, keep it brief and actionable
        if risk_level in ['critical', 'high']:
            # Already formatted by _extract_crisis_support
            return rag_content

        # For moderate risk with negative emotions, frame as supportive
        if risk_level == 'moderate' and dominant_emotion in ['sadness', 'fear', 'anger']:
            # Already formatted by _extract_coping_strategies
            # Add empathetic framing if it's just raw text
            if not any(intro in rag_content.lower() for intro in ['something that', 'here\'s', 'you could', 'one thing']):
                empathetic_frames = [
                    "I want to share something that might help: ",
                    "Here's something worth considering: ",
                    "This might offer some relief: ",
                ]
                return random.choice(empathetic_frames) + rag_content

        # For low-risk/positive conversations, make it informative and light
        if dominant_emotion in ['joy', 'love', 'neutral']:
            if not any(intro in rag_content.lower() for intro in ['something that', 'here\'s', 'you know']):
                light_frames = [
                    "Interesting fact: ",
                    "You might find this helpful: ",
                    "Here's something to keep in mind: ",
                ]
                return random.choice(light_frames) + rag_content

        return rag_content

    def _extract_relevant_snippet(self, context: str, max_length: int = 300) -> str:
        """Extract a relevant snippet from RAG context in a natural way"""
        if not context:
            return ""

        import re
        import random

        # Clean the context thoroughly
        clean_context = self._clean_rag_text(context)

        # Split into sentences
        sentences = [s.strip() for s in clean_context.split('.') if s.strip() and len(s.strip()) > 15]

        if not sentences:
            return ""

        # Filter out overly technical sentences
        conversational_sentences = []
        for sentence in sentences:
            # Skip research-heavy sentences
            if any(skip in sentence.lower() for skip in [
                'study found', 'research shows', 'data suggests', 'p <', 'statistical',
                'correlation', 'participants', 'et al', 'meta-analysis', 'n =',
                'hypothesis', 'methodology', 'sample size'
            ]):
                continue

            # Skip sentences that are too long or complex
            if len(sentence.split(',')) > 4:  # Too many clauses
                continue

            conversational_sentences.append(sentence)

        if not conversational_sentences:
            # If all sentences were technical, use original but simplify
            conversational_sentences = sentences[:3]

        # Build snippet from best sentences
        snippet = ""
        for sentence in conversational_sentences[:2]:  # Max 2 sentences for readability
            if len(snippet) + len(sentence) < max_length:
                snippet += sentence + ". "
            else:
                break

        snippet = snippet.strip()

        # Simplify the language
        if snippet:
            snippet = self._simplify_text(snippet)

            # Make it conversational - sound like you're sharing, not lecturing
            intro_phrases = [
                "Something that comes to mind - ",
                "Here's a thought: ",
                "You know, ",
                "From what I understand, ",
                "One thing worth knowing: ",
                "This might help: ",
                "I've learned that ",
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
