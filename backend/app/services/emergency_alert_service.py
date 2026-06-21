"""
Emergency Alert Service
Handles SMS and phone call alerts to emergency contacts via Twilio
"""
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
import logging
from datetime import datetime
from ..core.config import settings
from ..repositories.emergency_contact_repo import EmergencyContactRepository

logger = logging.getLogger(__name__)


class EmergencyAlertService:
    """Service for sending emergency alerts via SMS and phone calls"""

    def __init__(self, db: Session):
        self.db = db
        self.contact_repo = EmergencyContactRepository(db)

        # Initialize Twilio client
        try:
            self.twilio_client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_number = settings.TWILIO_PHONE_NUMBER
            logger.info("✓ Twilio client initialized successfully")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Twilio client: {e}")
            self.twilio_client = None

    def send_sms_alert(
        self,
        contact_phone: str,
        user_name: str,
        crisis_details: Dict,
        location: Optional[Dict] = None
    ) -> Dict:
        """
        Send SMS alert to emergency contact

        Args:
            contact_phone: Emergency contact's phone number
            user_name: Name of the user in crisis
            crisis_details: Dict with risk_level, risk_score, detected_emotion
            location: Optional dict with latitude, longitude

        Returns:
            Dict with success status and message_sid or error
        """
        if not self.twilio_client:
            return {
                "success": False,
                "error": "Twilio client not initialized. Check credentials."
            }

        try:
            # Build alert message
            message_body = self._build_sms_message(
                user_name, crisis_details, location
            )

            # Send SMS
            message = self.twilio_client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=contact_phone
            )

            logger.info(f"✓ SMS alert sent to {contact_phone}. SID: {message.sid}")

            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
                "sent_at": datetime.utcnow().isoformat()
            }

        except TwilioRestException as e:
            error_msg = f"Twilio error: {e.msg} (Code: {e.code})"
            logger.error(f"✗ {error_msg}")
            logger.error(f"✗ Contact phone: {contact_phone}, From: {self.from_number}")
            return {
                "success": False,
                "error": error_msg,
                "error_code": e.code
            }
        except Exception as e:
            logger.error(f"✗ Error sending SMS alert: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def make_voice_call(
        self,
        contact_phone: str,
        user_name: str,
        crisis_level: str
    ) -> Dict:
        """
        Make automated voice call to emergency contact

        Args:
            contact_phone: Emergency contact's phone number
            user_name: Name of the user in crisis
            crisis_level: Crisis severity (critical, high, moderate)

        Returns:
            Dict with success status and call_sid or error
        """
        if not self.twilio_client:
            return {
                "success": False,
                "error": "Twilio client not initialized"
            }

        try:
            # TwiML URL for voice message (you'll need to host this or use Twilio's TwiML Bins)
            twiml_url = f"{settings.API_URL}/api/emergency/voice-message?user={user_name}&level={crisis_level}"

            # Alternatively, use inline TwiML
            twiml = f"""
            <Response>
                <Say voice="alice">
                    This is an emergency alert from the Mental Health Chatbot.
                    {user_name} has been detected in a {crisis_level} risk crisis situation.
                    Please contact them immediately or call emergency services.
                    This is an automated message. Thank you.
                </Say>
            </Response>
            """

            # Make call
            call = self.twilio_client.calls.create(
                twiml=twiml,
                from_=self.from_number,
                to=contact_phone
            )

            logger.info(f"✓ Voice call initiated to {contact_phone}. SID: {call.sid}")

            return {
                "success": True,
                "call_sid": call.sid,
                "status": call.status,
                "initiated_at": datetime.utcnow().isoformat()
            }

        except TwilioRestException as e:
            logger.error(f"✗ Twilio error making call: {e}")
            return {
                "success": False,
                "error": f"Twilio error: {e.msg}",
                "error_code": e.code
            }
        except Exception as e:
            logger.error(f"✗ Error making voice call: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def send_comprehensive_alert(
        self,
        user_id: int,
        contact_id: int,
        crisis_details: Dict,
        location: Optional[Dict] = None,
        send_sms: bool = True,
        make_call: bool = False
    ) -> Dict:
        """
        Send comprehensive alert (SMS + optional voice call)

        Args:
            user_id: ID of user in crisis
            contact_id: ID of emergency contact to alert
            crisis_details: Crisis information
            location: Optional GPS coordinates
            send_sms: Whether to send SMS (default True)
            make_call: Whether to make voice call (default False, only for critical)

        Returns:
            Dict with results of SMS and/or call
        """
        try:
            # Get user and contact information
            from ..repositories.user_repo import UserRepository
            user_repo = UserRepository(self.db)
            user = user_repo.get_by_id(user_id)

            if not user:
                return {"success": False, "error": "User not found"}

            contact = self.contact_repo.get_by_id(contact_id)

            if not contact or contact.user_id != user_id:
                return {"success": False, "error": "Emergency contact not found"}

            results = {
                "user_id": user_id,
                "contact_id": contact_id,
                "contact_name": contact.name,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Send SMS alert
            if send_sms:
                sms_result = self.send_sms_alert(
                    contact_phone=contact.phone,
                    user_name=user.username or user.email,
                    crisis_details=crisis_details,
                    location=location
                )
                results["sms"] = sms_result

            # Make voice call for critical situations
            if make_call or crisis_details.get("risk_level") == "critical":
                call_result = self.make_voice_call(
                    contact_phone=contact.phone,
                    user_name=user.username or user.email,
                    crisis_level=crisis_details.get("risk_level", "high")
                )
                results["call"] = call_result

            # Log the alert
            self._log_alert(user_id, contact_id, crisis_details, results)

            return results

        except Exception as e:
            logger.error(f"✗ Error sending comprehensive alert: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _build_sms_message(
        self,
        user_name: str,
        crisis_details: Dict,
        location: Optional[Dict] = None
    ) -> str:
        """Build SMS message text"""
        risk_level = crisis_details.get("risk_level", "unknown").upper()
        risk_score = crisis_details.get("risk_score", 0) * 100
        emotion = crisis_details.get("detected_emotion", "distressed")

        message = f"🚨 MENTAL HEALTH CRISIS ALERT\n\n"
        message += f"User: {user_name}\n"
        message += f"Risk Level: {risk_level}\n"
        message += f"Risk Score: {risk_score:.1f}%\n"
        message += f"Emotional State: {emotion}\n"

        if location:
            lat = location.get("latitude")
            lon = location.get("longitude")
            if lat and lon:
                message += f"\n📍 Location: {lat:.6f}, {lon:.6f}\n"
                message += f"Map: https://maps.google.com/?q={lat},{lon}\n"

        message += f"\n⚠️ Please contact {user_name} immediately or call emergency services.\n"
        message += f"\nSent by Mental Health Chatbot at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"

        return message

    def _log_alert(
        self,
        user_id: int,
        contact_id: int,
        crisis_details: Dict,
        results: Dict
    ):
        """Log alert to database for tracking"""
        try:
            # You can create an AlertLog model to track all alerts sent
            logger.info(
                f"Alert sent - User: {user_id}, Contact: {contact_id}, "
                f"Risk: {crisis_details.get('risk_level')}, "
                f"SMS: {results.get('sms', {}).get('success')}, "
                f"Call: {results.get('call', {}).get('success')}"
            )
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")

    def get_user_emergency_contacts(self, user_id: int) -> List:
        """Get all emergency contacts for a user"""
        return self.contact_repo.get_user_contacts(user_id)

    def test_twilio_connection(self) -> Dict:
        """Test Twilio connection and credentials"""
        if not self.twilio_client:
            return {
                "success": False,
                "error": "Twilio client not initialized"
            }

        try:
            # Fetch account info to verify credentials
            account = self.twilio_client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()

            return {
                "success": True,
                "account_sid": account.sid,
                "account_status": account.status,
                "from_number": self.from_number
            }
        except TwilioRestException as e:
            return {
                "success": False,
                "error": f"Twilio authentication failed: {e.msg}",
                "error_code": e.code
            }
