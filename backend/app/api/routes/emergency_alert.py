from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import logging
from ...core.database import get_db
from ...services.emergency_alert_service import EmergencyAlertService
from ..dependencies import get_current_user_id

router = APIRouter()


class EmergencyAlertRequest(BaseModel):
    """Request model for sending emergency alert"""
    contact_id: int
    risk_level: str
    risk_score: float
    detected_emotion: str
    crisis_reason: str = "Crisis detected by AI system"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    send_sms: bool = True
    make_call: bool = False


class EmergencyAlertResponse(BaseModel):
    """Response model for emergency alert"""
    success: bool
    message: str
    sms_sent: Optional[bool] = None
    call_made: Optional[bool] = None
    details: Optional[dict] = None


@router.post("/send", response_model=EmergencyAlertResponse)
def send_emergency_alert(
    alert_request: EmergencyAlertRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Send emergency alert to specified contact

    Endpoint: POST /api/emergency-alert/send

    Headers:
    - Authorization: Bearer <access_token>

    Request Body:
    - contact_id: ID of emergency contact
    - risk_level: Crisis level (critical, high, moderate, low)
    - risk_score: Risk score (0.0-1.0)
    - detected_emotion: Detected emotion
    - crisis_reason: Optional reason for alert
    - latitude: Optional GPS latitude
    - longitude: Optional GPS longitude
    - send_sms: Whether to send SMS (default True)
    - make_call: Whether to make voice call (default False)

    Returns:
    - Success status and details
    """
    try:
        service = EmergencyAlertService(db)
        logger = logging.getLogger(__name__)
        logger.info(f"📱 Sending emergency alert - Contact ID: {alert_request.contact_id}, Risk: {alert_request.risk_level}")

        # Build crisis details
        crisis_details = {
            "risk_level": alert_request.risk_level,
            "risk_score": alert_request.risk_score,
            "detected_emotion": alert_request.detected_emotion,
            "crisis_reason": alert_request.crisis_reason
        }

        # Build location if provided
        location = None
        if alert_request.latitude and alert_request.longitude:
            location = {
                "latitude": alert_request.latitude,
                "longitude": alert_request.longitude
            }

        # Send comprehensive alert
        result = service.send_comprehensive_alert(
            user_id=user_id,
            contact_id=alert_request.contact_id,
            crisis_details=crisis_details,
            location=location,
            send_sms=alert_request.send_sms,
            make_call=alert_request.make_call
        )

        logger.info(f"📊 Alert result: {result}")

        if result.get("success") == False and "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )

        # Extract SMS and call results
        sms_result = result.get("sms", {})
        call_result = result.get("call", {})

        # Check if SMS actually succeeded
        if alert_request.send_sms and not sms_result.get("success"):
            error_msg = sms_result.get("error", "Unknown SMS error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"SMS failed: {error_msg}"
            )

        return EmergencyAlertResponse(
            success=True,
            message=f"Emergency alert sent to {result.get('contact_name')}",
            sms_sent=sms_result.get("success"),
            call_made=call_result.get("success") if call_result else None,
            details=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send emergency alert: {str(e)}"
        )


@router.get("/contacts")
def get_emergency_contacts(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all emergency contacts for current user

    Endpoint: GET /api/emergency-alert/contacts

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - List of emergency contacts
    """
    try:
        service = EmergencyAlertService(db)
        contacts = service.get_user_emergency_contacts(user_id)

        return {
            "contacts": [
                {
                    "id": contact.id,
                    "name": contact.name,
                    "phone": contact.phone,
                    "relationship_type": contact.relationship_type,
                    "is_primary": contact.is_primary
                }
                for contact in contacts
            ],
            "total": len(contacts)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emergency contacts: {str(e)}"
        )


@router.get("/test-whatsapp")
def test_whatsapp_connection(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Test WhatsApp Business API connection and credentials

    Endpoint: GET /api/emergency-alert/test-whatsapp

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - WhatsApp connection status
    """
    try:
        service = EmergencyAlertService(db)
        result = service.test_whatsapp_connection()

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=result.get("error", "WhatsApp connection failed")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test WhatsApp connection: {str(e)}"
        )


@router.get("/test-twilio")
def test_twilio_connection(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Deprecated: Use /test-whatsapp instead
    """
    return test_whatsapp_connection(user_id, db)
