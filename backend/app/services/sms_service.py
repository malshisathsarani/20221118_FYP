"""
SMS Service for Emergency Alerts
Sends SMS notifications to emergency contacts using Twilio
"""
from typing import List, Optional, Dict
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from ..core.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS alerts via Twilio"""

    def __init__(self):
        """Initialize Twilio client"""
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_PHONE_NUMBER

        # Initialize client only if credentials are provided
        if self.account_sid and self.auth_token and self.from_number:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self.enabled = True
                logger.info("✓ Twilio SMS service initialized successfully")
            except Exception as e:
                logger.error(f"✗ Failed to initialize Twilio client: {e}")
                self.client = None
                self.enabled = False
        else:
            logger.warning("⚠️ Twilio credentials not configured - SMS alerts disabled")
            self.client = None
            self.enabled = False

    def send_crisis_alert(
        self,
        to_number: str,
        user_name: str,
        crisis_level: str,
        message_preview: Optional[str] = None,
        location: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Send crisis alert SMS to emergency contact

        Args:
            to_number: Phone number to send to (E.164 format, e.g., +15551234567)
            user_name: Name of user in crisis
            crisis_level: Risk level (high, critical)
            message_preview: Optional preview of user's message
            location: Optional dict with lat/long coordinates

        Returns:
            Dict with status and message_sid or error
        """
        if not self.enabled:
            logger.warning("SMS service not enabled - skipping alert")
            return {
                "success": False,
                "error": "SMS service not configured",
                "message_sid": None
            }

        # Build alert message
        alert_message = self._build_crisis_message(
            user_name=user_name,
            crisis_level=crisis_level,
            message_preview=message_preview,
            location=location
        )

        try:
            # Send SMS via Twilio
            message = self.client.messages.create(
                body=alert_message,
                from_=self.from_number,
                to=to_number
            )

            logger.info(f"✓ Crisis alert SMS sent to {to_number} - SID: {message.sid}")

            return {
                "success": True,
                "message_sid": message.sid,
                "to_number": to_number,
                "status": message.status
            }

        except TwilioRestException as e:
            logger.error(f"✗ Twilio error sending SMS to {to_number}: {e.msg} (code: {e.code})")
            return {
                "success": False,
                "error": f"Twilio error: {e.msg}",
                "error_code": e.code,
                "message_sid": None
            }
        except Exception as e:
            logger.error(f"✗ Unexpected error sending SMS to {to_number}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_sid": None
            }

    def send_bulk_crisis_alerts(
        self,
        contacts: List[Dict],
        user_name: str,
        crisis_level: str,
        message_preview: Optional[str] = None,
        location: Optional[Dict[str, float]] = None
    ) -> List[Dict]:
        """
        Send crisis alerts to multiple emergency contacts

        Args:
            contacts: List of contact dicts with 'phone' and 'name' keys
            user_name: Name of user in crisis
            crisis_level: Risk level
            message_preview: Optional message preview
            location: Optional location data

        Returns:
            List of results for each contact
        """
        results = []

        for contact in contacts:
            phone = contact.get('phone')
            contact_name = contact.get('name', 'Emergency Contact')

            if not phone:
                logger.warning(f"Skipping contact '{contact_name}' - no phone number")
                results.append({
                    "contact_name": contact_name,
                    "success": False,
                    "error": "No phone number provided"
                })
                continue

            # Format phone number to E.164 if needed
            formatted_phone = self._format_phone_number(phone)

            if not formatted_phone:
                logger.warning(f"Skipping contact '{contact_name}' - invalid phone: {phone}")
                results.append({
                    "contact_name": contact_name,
                    "phone": phone,
                    "success": False,
                    "error": "Invalid phone number format"
                })
                continue

            # Send alert
            result = self.send_crisis_alert(
                to_number=formatted_phone,
                user_name=user_name,
                crisis_level=crisis_level,
                message_preview=message_preview,
                location=location
            )

            result['contact_name'] = contact_name
            results.append(result)

        # Log summary
        success_count = sum(1 for r in results if r.get('success'))
        logger.info(f"Crisis alert batch: {success_count}/{len(contacts)} sent successfully")

        return results

    def _build_crisis_message(
        self,
        user_name: str,
        crisis_level: str,
        message_preview: Optional[str] = None,
        location: Optional[Dict[str, float]] = None
    ) -> str:
        """Build crisis alert SMS message"""

        # Severity-based opening
        if crisis_level == "critical":
            opening = f"🚨 URGENT: {user_name} may be in immediate danger."
        else:
            opening = f"⚠️ ALERT: {user_name} is experiencing a mental health crisis."

        message_parts = [opening]

        # Add context if available
        if message_preview:
            preview = message_preview[:100] + "..." if len(message_preview) > 100 else message_preview
            message_parts.append(f"\nRecent message: \"{preview}\"")

        # Add location if available
        if location and location.get('latitude') and location.get('longitude'):
            lat = location['latitude']
            lng = location['longitude']
            maps_url = f"https://maps.google.com/?q={lat},{lng}"
            message_parts.append(f"\nLocation: {maps_url}")

        # Add action instructions
        message_parts.append(f"\n\nPlease check on them immediately or call emergency services (911) if needed.")
        message_parts.append(f"\nNational Crisis Line: 988")

        # Add timestamp
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        message_parts.append(f"\n\nAlert sent: {timestamp}")

        return "".join(message_parts)

    def _format_phone_number(self, phone: str) -> Optional[str]:
        """
        Format phone number to E.164 format (+15551234567)

        Handles:
        - US numbers: (555) 123-4567, 555-123-4567, 5551234567
        - International: Already in E.164 format

        Returns formatted number or None if invalid
        """
        import re

        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)

        # If already has country code (starts with 1 and has 11 digits)
        if len(digits) == 11 and digits.startswith('1'):
            return f"+{digits}"

        # US number without country code (10 digits)
        if len(digits) == 10:
            return f"+1{digits}"

        # International number already with + prefix
        if phone.startswith('+'):
            return phone

        # Unknown format
        logger.warning(f"Could not format phone number: {phone}")
        return None

    def send_test_sms(self, to_number: str) -> Dict:
        """
        Send test SMS to verify Twilio configuration

        Args:
            to_number: Phone number to test (E.164 format)

        Returns:
            Dict with success status
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "SMS service not configured"
            }

        try:
            message = self.client.messages.create(
                body="Test message from Mental Health Chatbot. SMS alerts are working correctly! ✓",
                from_=self.from_number,
                to=to_number
            )

            logger.info(f"✓ Test SMS sent to {to_number} - SID: {message.sid}")

            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status
            }

        except TwilioRestException as e:
            logger.error(f"✗ Twilio test error: {e.msg}")
            return {
                "success": False,
                "error": e.msg,
                "error_code": e.code
            }


# Singleton instance
_sms_service_instance = None


def get_sms_service() -> SMSService:
    """Get or create SMS service singleton"""
    global _sms_service_instance
    if _sms_service_instance is None:
        _sms_service_instance = SMSService()
    return _sms_service_instance
