from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from ..models.user import User


class ProfileRepository:
    """Repository for Profile-related database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_profile_by_user_id(self, user_id: int) -> Optional[User]:
        """Get user profile by user ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def update_profile_info(
        self,
        user: User,
        full_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        """Update user profile information"""
        if full_name is not None:
            user.full_name = full_name
        if phone_number is not None:
            user.phone_number = phone_number
        if bio is not None:
            user.bio = bio
        if avatar_url is not None:
            user.avatar_url = avatar_url

        self.db.commit()
        self.db.refresh(user)
        return user

    def update_preferences(
        self,
        user: User,
        notifications_enabled: Optional[bool] = None,
        email_notifications: Optional[bool] = None
    ) -> User:
        """Update user notification preferences"""
        if notifications_enabled is not None:
            user.notifications_enabled = notifications_enabled
        if email_notifications is not None:
            user.email_notifications = email_notifications

        self.db.commit()
        self.db.refresh(user)
        return user

    def update_privacy_settings(
        self,
        user: User,
        data_sharing_consent: Optional[bool] = None,
        analytics_consent: Optional[bool] = None
    ) -> User:
        """Update user privacy settings"""
        if data_sharing_consent is not None:
            user.data_sharing_consent = data_sharing_consent
        if analytics_consent is not None:
            user.analytics_consent = analytics_consent

        self.db.commit()
        self.db.refresh(user)
        return user

    def update_profile_fields(self, user: User, update_data: Dict[str, Any]) -> User:
        """Generic method to update multiple profile fields at once"""
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user
