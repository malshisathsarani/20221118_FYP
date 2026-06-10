from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...repositories.chat_repo import ChatRepository
from ..dependencies import get_current_user_id

router = APIRouter(prefix="/crisis", tags=["Crisis Detection"])


@router.get("/alerts")
def get_crisis_alerts(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all crisis alerts for the current user"""
    chat_repo = ChatRepository(db)
    crisis_chats = chat_repo.get_crisis_chats(user_id)

    alerts = []
    for chat in crisis_chats:
        severity_map = {0: None, 1: "mild", 2: "moderate", 3: "severe"}
        alerts.append({
            "id": chat.id,
            "session_id": chat.session_id,
            "message": chat.message,
            "severity": severity_map.get(chat.is_crisis),
            "crisis_score": chat.crisis_score,
            "detected_at": chat.created_at
        })

    return {"alerts": alerts, "total": len(alerts)}


@router.get("/resources")
def get_crisis_resources():
    """Get mental health crisis resources"""
    resources = {
        "emergency": {
            "name": "National Suicide Prevention Lifeline",
            "phone": "988",
            "available": "24/7"
        },
        "crisis_text": {
            "name": "Crisis Text Line",
            "text": "HELLO to 741741",
            "available": "24/7"
        },
        "online_resources": [
            {
                "name": "SAMHSA National Helpline",
                "phone": "1-800-662-4357",
                "description": "Treatment referral and information service"
            },
            {
                "name": "NAMI Helpline",
                "phone": "1-800-950-6264",
                "description": "Information, resource referrals, and support"
            }
        ],
        "warning": "If you're in immediate danger, please call 911 or go to your nearest emergency room."
    }

    return resources
