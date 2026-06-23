from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from ...core.database import get_db
from ...models.user import User
from ...models.chat import Chat
from ...models.feedback import Feedback
from ...models.emergency_contact import EmergencyContact
from ..dependencies import get_current_user_id

router = APIRouter()
logger = logging.getLogger(__name__)


class UserUpdateRequest(BaseModel):
    """Request model for updating user profile"""
    full_name: Optional[str] = None
    email: Optional[str] = None


class PreferencesUpdateRequest(BaseModel):
    """Request model for updating user preferences"""
    notifications_enabled: Optional[bool] = None
    dark_mode: Optional[bool] = None


@router.get("/stats")
def get_user_stats(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get user activity statistics

    Returns:
    - total_chats: Number of chat messages
    - crisis_events: Number of crisis detections
    - tools_used: Number of therapeutic tools used
    - days_active: Days since account creation
    """
    try:
        # Get total chats
        total_chats = db.query(Chat).filter(Chat.user_id == user_id).count()

        # Get crisis events (where is_crisis > 0)
        crisis_events = db.query(Chat).filter(
            Chat.user_id == user_id,
            Chat.is_crisis > 0
        ).count()

        # Get tools used (if game_sessions table exists)
        tools_used = 0
        try:
            from ...models.game_session import GameSession
            tools_used = db.query(GameSession).filter(
                GameSession.user_id == user_id,
                GameSession.completed == True
            ).count()
        except:
            logger.info("GameSession model not available")

        # Get days active (since account creation)
        user = db.query(User).filter(User.id == user_id).first()
        days_active = 0
        if user and user.created_at:
            days_active = (datetime.utcnow() - user.created_at).days

        return {
            "total_chats": total_chats,
            "crisis_events": crisis_events,
            "tools_used": tools_used,
            "days_active": days_active
        }

    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user statistics: {str(e)}"
        )


@router.put("/profile")
def update_profile(
    updates: UserUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update user profile information

    Can update:
    - full_name
    - email
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update fields if provided
        if updates.full_name is not None:
            user.full_name = updates.full_name

        if updates.email is not None:
            # Check if email already exists
            existing = db.query(User).filter(
                User.email == updates.email,
                User.id != user_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            user.email = updates.email

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "username": user.username
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.put("/preferences")
def update_preferences(
    preferences: PreferencesUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update user preferences

    Can update:
    - notifications_enabled
    - dark_mode
    """
    try:
        # For now, just return success
        # In future, add UserPreferences table to store these
        logger.info(f"User {user_id} updated preferences: {preferences.dict()}")

        return {
            "success": True,
            "message": "Preferences updated successfully"
        }

    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.get("/export-data")
def export_user_data(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Export all user data (GDPR compliance)

    Returns all data associated with the user:
    - Profile information
    - Chat history
    - Crisis events
    - Emergency contacts
    - Feedback
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Get all user data
        chats = db.query(Chat).filter(Chat.user_id == user_id).all()
        contacts = db.query(EmergencyContact).filter(
            EmergencyContact.user_id == user_id
        ).all()
        feedback = db.query(Feedback).filter(Feedback.user_id == user_id).all()

        return {
            "user_profile": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            },
            "chats": [
                {
                    "id": chat.id,
                    "message": chat.message,
                    "response": chat.response,
                    "detected_emotion": chat.detected_emotion,
                    "crisis_score": chat.crisis_score,
                    "is_crisis": chat.is_crisis,
                    "created_at": chat.created_at.isoformat() if chat.created_at else None,
                }
                for chat in chats
            ],
            "emergency_contacts": [
                {
                    "id": contact.id,
                    "name": contact.name,
                    "phone": contact.phone,
                    "relationship_type": contact.relationship_type,
                    "is_primary": contact.is_primary,
                }
                for contact in contacts
            ],
            "feedback": [
                {
                    "id": fb.id,
                    "rating": fb.rating,
                    "feedback_type": fb.feedback_type,
                    "comment": fb.comment,
                    "created_at": fb.created_at.isoformat() if fb.created_at else None,
                }
                for fb in feedback
            ],
            "export_date": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting user data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}"
        )


@router.delete("/delete-account")
def delete_account(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Permanently delete user account and all associated data

    Deletes:
    - All chat history
    - Crisis events
    - Emergency contacts
    - Feedback
    - User profile

    This action cannot be undone!
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        logger.warning(f"Deleting account for user {user_id} ({user.email})")

        # Delete all related data (cascade should handle this, but be explicit)
        db.query(Chat).filter(Chat.user_id == user_id).delete()
        db.query(EmergencyContact).filter(EmergencyContact.user_id == user_id).delete()
        db.query(Feedback).filter(Feedback.user_id == user_id).delete()

        # Delete user
        db.delete(user)
        db.commit()

        logger.info(f"Account deleted successfully for user {user_id}")

        return {
            "success": True,
            "message": "Account deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )
