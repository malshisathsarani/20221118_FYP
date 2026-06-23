"""
WhatsApp Business API Service
Sends crisis alerts via WhatsApp using Meta's Cloud API
"""
import requests
import logging
from typing import Dict, Optional
from datetime import datetime
from ..core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service for sending WhatsApp messages via Meta Cloud API"""

    def __init__(self):
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.api_version = settings.WHATSAPP_API_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"

        # Check if credentials are configured
        if not self.phone_number_id or not self.access_token:
            logger.warning("⚠️ WhatsApp credentials not configured in .env")
        else:
            logger.info("✓ WhatsApp service initialized successfully")

    def send_crisis_alert(
        self,
        to_number: str,
        user_name: str,
        crisis_level: str,
        risk_score: float,
        detected_emotion: str,
        crisis_reason: str = "Crisis indicators detected",
        location: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Send crisis alert via WhatsApp

        Args:
            to_number: Recipient WhatsApp number (format: 94771234567)
            user_name: Name of user in crisis
            crisis_level: Crisis severity (critical, high, moderate, low)
            risk_score: Risk score (0.0-1.0)
            detected_emotion: Detected emotional state
            crisis_reason: Reason for alert
            location: Optional GPS coordinates {latitude, longitude}

        Returns:
            Dict with success status and message ID or error
        """
        if not self.access_token or not self.phone_number_id:
            return {
                "success": False,
                "error": "WhatsApp API not configured. Check .env file."
            }

        try:
            # Build message text
            message_text = self._build_crisis_message(
                user_name=user_name,
                crisis_level=crisis_level,
                risk_score=risk_score,
                detected_emotion=detected_emotion,
                crisis_reason=crisis_reason,
                location=location
            )

            # Format phone number (remove +, spaces, hyphens, parentheses)
            formatted_number = to_number.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

            # Send WhatsApp message
            result = self._send_text_message(
                to=formatted_number,
                message=message_text
            )

            if result.get("success"):
                logger.info(f"✓ WhatsApp alert sent to {formatted_number}")
                logger.info(f"  Message ID: {result.get('message_id')}")
            else:
                logger.error(f"✗ WhatsApp alert failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"✗ Error sending WhatsApp alert: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _send_text_message(self, to: str, message: str) -> Dict:
        """
        Send text message via WhatsApp Cloud API

        Args:
            to: Recipient phone number (without +)
            message: Message text to send

        Returns:
            Dict with success status and message_id or error
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": True,  # Enable link previews
                "body": message
            }
        }

        try:
            logger.info(f"📤 Sending WhatsApp message to {to}")
            logger.info(f"📝 Message preview: {message[:100]}...")
            logger.info(f"🔗 API URL: {self.base_url}")
            logger.info(f"📱 Formatted recipient: {to}")

            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=10
            )

            logger.info(f"📊 Response status: {response.status_code}")
            response_data = response.json()
            logger.info(f"📊 Response data: {response_data}")

            if response.status_code == 200:
                message_id = response_data.get("messages", [{}])[0].get("id")
                return {
                    "success": True,
                    "message_id": message_id,
                    "recipient": to,
                    "sent_at": datetime.utcnow().isoformat()
                }
            else:
                error_message = response_data.get("error", {}).get("message", "Unknown error")
                error_code = response_data.get("error", {}).get("code", "unknown")
                logger.error(f"✗ WhatsApp API error: {error_message} (Code: {error_code})")
                return {
                    "success": False,
                    "error": error_message,
                    "error_code": error_code
                }

        except requests.exceptions.Timeout:
            logger.error("✗ WhatsApp API request timed out")
            return {
                "success": False,
                "error": "Request timed out"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ WhatsApp API request failed: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"✗ Unexpected error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _build_crisis_message(
        self,
        user_name: str,
        crisis_level: str,
        risk_score: float,
        detected_emotion: str,
        crisis_reason: str,
        location: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Build crisis alert message text

        Returns:
            Formatted WhatsApp message
        """
        # Emoji and tone based on crisis level
        if crisis_level.lower() == "critical":
            emoji = "🆘"
            urgency = "urgent attention"
            greeting = "Hi, this is important."
        elif crisis_level.lower() == "high":
            emoji = "⚠️"
            urgency = "immediate support"
            greeting = "Hi, I wanted to let you know."
        else:  # moderate or low
            emoji = "💙"
            urgency = "some support"
            greeting = "Hi, just a heads up."

        # Build friendly message
        message = f"{emoji} *{greeting}*\n\n"
        message += f"I'm reaching out because *{user_name}* might need {urgency} right now.\n\n"

        # Add emotional state in a caring way
        emotion_text = {
            "sadness": "They're going through a really tough time and feeling very down.",
            "fear": "They seem to be experiencing a lot of worry and anxiety.",
            "anger": "They're feeling really frustrated and overwhelmed.",
            "neutral": "They might be struggling with something.",
        }
        message += f"💭 {emotion_text.get(detected_emotion.lower(), 'They seem to be having a difficult moment.')}\n\n"

        # Add gentle action request
        if crisis_level.lower() in ["critical", "high"]:
            message += f"🤝 *Please reach out to {user_name} as soon as you can.* A friendly check-in could make a real difference right now.\n\n"
            message += f"If you're unable to reach them, please consider contacting emergency services or a crisis helpline.\n"
        else:
            message += f"🤝 *When you have a moment, please check in with {user_name}.* Just knowing someone cares can really help.\n"

        # Add timestamp
        current_time = datetime.utcnow().strftime("%I:%M %p, %B %d")
        message += f"\n🕒 {current_time}\n"

        # Friendly footer
        message += f"\n_This message was sent automatically by {user_name}'s mental health support app._"

        return message

    def send_template_message(self, to: str, template_name: str = "hello_world") -> Dict:
        """
        Send pre-approved template message (for testing)

        Args:
            to: Recipient phone number
            template_name: Template name (default: hello_world)

        Returns:
            Dict with success status
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": to.replace('+', '').replace(' ', ''),
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": "en_US"
                }
            }
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": response.json()
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def test_connection(self) -> Dict:
        """
        Test WhatsApp API connection

        Returns:
            Dict with connection status
        """
        if not self.access_token or not self.phone_number_id:
            return {
                "success": False,
                "error": "WhatsApp credentials not configured"
            }

        try:
            # Test by fetching phone number info
            url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "phone_number_id": self.phone_number_id,
                    "verified_name": data.get("verified_name"),
                    "display_phone_number": data.get("display_phone_number")
                }
            else:
                return {
                    "success": False,
                    "error": response.json()
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
