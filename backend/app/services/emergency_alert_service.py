"""
Emergency Alert Service
Handles WhatsApp alerts to emergency contacts via Meta WhatsApp Business API
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
import logging
from datetime import datetime
from ..core.config import settings
from ..repositories.emergency_contact_repo import EmergencyContactRepository
from .whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)


class EmergencyAlertService:
    """Service for sending emergency alerts via WhatsApp"""

    def __init__(self, db: Session):
        self.db = db
        self.contact_repo = EmergencyContactRepository(db)

        # Initialize WhatsApp service
        try:
            self.whatsapp_service = WhatsAppService()
            logger.info("✓ WhatsApp service initialized successfully")
        except Exception as e:
            logger.error(f"✗ Failed to initialize WhatsApp service: {e}")
            self.whatsapp_service = None

    def send_whatsapp_alert(
        self,
        contact_phone: str,
        user_name: str,
        crisis_details: Dict,
        location: Optional[Dict] = None
    ) -> Dict:
        """
        Send WhatsApp alert to emergency contact

        Args:
            contact_phone: Emergency contact's WhatsApp number
            user_name: Name of the user in crisis
            crisis_details: Dict with risk_level, risk_score, detected_emotion, crisis_reason
            location: Optional dict with latitude, longitude

        Returns:
            Dict with success status and message_id or error
        """
        if not self.whatsapp_service:
            return {
                "success": False,
                "error": "WhatsApp service not initialized. Check credentials."
            }

        try:
            # Send WhatsApp alert
            result = self.whatsapp_service.send_crisis_alert(
                to_number=contact_phone,
                user_name=user_name,
                crisis_level=crisis_details.get("risk_level", "high"),
                risk_score=crisis_details.get("risk_score", 0.0),
                detected_emotion=crisis_details.get("detected_emotion", "distressed"),
                crisis_reason=crisis_details.get("crisis_reason", "Crisis indicators detected"),
                location=location
            )

            return result

        except Exception as e:
            logger.error(f"✗ Error sending WhatsApp alert: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # Alias for backward compatibility
    def send_sms_alert(self, *args, **kwargs) -> Dict:
        """Alias for send_whatsapp_alert (backward compatibility)"""
        return self.send_whatsapp_alert(*args, **kwargs)

    def make_voice_call(
        self,
        contact_phone: str,
        user_name: str,
        crisis_level: str
    ) -> Dict:
        """
        Voice call feature deprecated (WhatsApp replaced Twilio)
        Now sends a high-priority WhatsApp message instead

        Args:
            contact_phone: Emergency contact's WhatsApp number
            user_name: Name of the user in crisis
            crisis_level: Crisis severity (critical, high, moderate)

        Returns:
            Dict with success status indicating WhatsApp sent
        """
        logger.info("ℹ️ Voice call deprecated - sending high-priority WhatsApp instead")

        # Send high-priority WhatsApp message instead
        crisis_details = {
            "risk_level": crisis_level,
            "risk_score": 0.9 if crisis_level == "critical" else 0.75,
            "detected_emotion": "severe distress",
            "crisis_reason": "URGENT: Immediate attention required"
        }

        return self.send_whatsapp_alert(
            contact_phone=contact_phone,
            user_name=user_name,
            crisis_details=crisis_details
        )

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
        Send comprehensive alert via WhatsApp

        Args:
            user_id: ID of user in crisis
            contact_id: ID of emergency contact to alert
            crisis_details: Crisis information
            location: Optional GPS coordinates
            send_sms: Whether to send WhatsApp (default True)
            make_call: Deprecated (sends high-priority WhatsApp instead)

        Returns:
            Dict with results of WhatsApp message
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
                "success": True,
                "user_id": user_id,
                "contact_id": contact_id,
                "contact_name": contact.name,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Send WhatsApp alert (replaces SMS)
            if send_sms:
                whatsapp_result = self.send_whatsapp_alert(
                    contact_phone=contact.phone,
                    user_name=user.username or user.email,
                    crisis_details=crisis_details,
                    location=location
                )
                results["whatsapp"] = whatsapp_result
                results["sms"] = whatsapp_result  # For backward compatibility

                # If WhatsApp was requested but failed, mark the whole operation as failed
                if not whatsapp_result.get("success"):
                    results["success"] = False
                    results["error"] = whatsapp_result.get("error", "WhatsApp failed")

            # For critical situations, log that voice call is deprecated
            if make_call or crisis_details.get("risk_level") == "critical":
                logger.info("ℹ️ Voice call requested but deprecated - WhatsApp already sent")
                results["call"] = {
                    "success": True,
                    "note": "Voice call deprecated - WhatsApp sent instead"
                }

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
        """Deprecated: WhatsApp service builds messages now"""
        logger.warning("⚠️ _build_sms_message is deprecated - use WhatsApp service")
        return f"Crisis alert for {user_name}"

    def _log_alert(
        self,
        user_id: int,
        contact_id: int,
        crisis_details: Dict,
        results: Dict
    ):
        """Log alert to database for tracking"""
        try:
            # Log WhatsApp alert result
            logger.info(
                f"📱 Alert sent - User: {user_id}, Contact: {contact_id}, "
                f"Risk: {crisis_details.get('risk_level')}, "
                f"WhatsApp: {results.get('whatsapp', {}).get('success')}"
            )
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")

    def get_user_emergency_contacts(self, user_id: int) -> List:
        """Get all emergency contacts for a user"""
        return self.contact_repo.get_user_contacts(user_id)

    def send_alert_to_all_contacts(
        self,
        user_id: int,
        crisis_details: Dict,
        message_preview: str,
        location: Optional[Dict] = None
    ) -> Dict:
        """
        Send WhatsApp alerts to all emergency contacts for a user

        Args:
            user_id: ID of user in crisis
            crisis_details: Dict with risk_level, risk_score, detected_emotion, crisis_reason
            message_preview: Preview of the crisis message
            location: Optional GPS coordinates

        Returns:
            Dict with results including success status, alerts sent/failed counts
        """
        try:
            # Get all emergency contacts for this user
            contacts = self.get_user_emergency_contacts(user_id)

            if not contacts:
                logger.warning(f"⚠️ No emergency contacts found for user {user_id}")
                return {
                    "success": False,
                    "error": "No emergency contacts configured",
                    "total_contacts": 0,
                    "alerts_sent": 0,
                    "alerts_failed": 0
                }

            # Get user info
            from ..repositories.user_repo import UserRepository
            user_repo = UserRepository(self.db)
            user = user_repo.get_by_id(user_id)
            user_name = user.username if user else f"User {user_id}"

            # Send alert to each contact
            results = []
            alerts_sent = 0
            alerts_failed = 0

            for contact in contacts:
                logger.info(f"📤 Sending alert to {contact.name} ({contact.phone})")

                result = self.send_whatsapp_alert(
                    contact_phone=contact.phone,
                    user_name=user_name,
                    crisis_details=crisis_details,
                    location=location
                )

                results.append({
                    "contact_id": contact.id,
                    "contact_name": contact.name,
                    "contact_phone": contact.phone,
                    "success": result.get("success"),
                    "message_id": result.get("message_id"),
                    "error": result.get("error")
                })

                if result.get("success"):
                    alerts_sent += 1
                    logger.info(f"✓ Alert sent to {contact.name}")
                else:
                    alerts_failed += 1
                    logger.error(f"✗ Alert failed for {contact.name}: {result.get('error')}")

            return {
                "success": alerts_sent > 0,  # Success if at least one alert sent
                "total_contacts": len(contacts),
                "alerts_sent": alerts_sent,
                "alerts_failed": alerts_failed,
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"✗ Error in send_alert_to_all_contacts: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_contacts": 0,
                "alerts_sent": 0,
                "alerts_failed": 0
            }

    def test_whatsapp_connection(self) -> Dict:
        """Test WhatsApp API connection and credentials"""
        if not self.whatsapp_service:
            return {
                "success": False,
                "error": "WhatsApp service not initialized"
            }

        return self.whatsapp_service.test_connection()

    # Deprecated - for backward compatibility
    def test_twilio_connection(self) -> Dict:
        """Deprecated: Use test_whatsapp_connection instead"""
        logger.warning("⚠️ test_twilio_connection is deprecated - use test_whatsapp_connection")
        return self.test_whatsapp_connection()
