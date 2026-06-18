from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status
from ..repositories.profile_repository import ProfileRepository
from ..repositories.user_repository import UserRepository
from ..schemas.profile import (
    ProfileResponse,
    ProfileUpdate,
    PreferencesUpdate,
    PrivacySettingsUpdate
)
from ..models.user import User


class ProfileService:
    """Service layer for profile-related business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.profile_repo = ProfileRepository(db)
        self.user_repo = UserRepository(db)

    def get_user_profile(self, user_id: int) -> User:
        """Get user profile by user ID"""
        user = self.profile_repo.get_profile_by_user_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        return user

    def update_profile(self, user_id: int, profile_data: ProfileUpdate) -> User:
        """Update user profile information"""
        user = self.get_user_profile(user_id)

        # Update only fields that are provided
        update_dict = profile_data.model_dump(exclude_unset=True)

        if not update_dict:
            return user

        updated_user = self.profile_repo.update_profile_info(
            user=user,
            full_name=update_dict.get("full_name"),
            phone_number=update_dict.get("phone_number"),
            bio=update_dict.get("bio"),
            avatar_url=update_dict.get("avatar_url")
        )

        return updated_user

    def update_preferences(self, user_id: int, preferences_data: PreferencesUpdate) -> User:
        """Update user notification preferences"""
        user = self.get_user_profile(user_id)

        # Update only fields that are provided
        update_dict = preferences_data.model_dump(exclude_unset=True)

        if not update_dict:
            return user

        updated_user = self.profile_repo.update_preferences(
            user=user,
            notifications_enabled=update_dict.get("notifications_enabled"),
            email_notifications=update_dict.get("email_notifications")
        )

        return updated_user

    def update_privacy_settings(self, user_id: int, privacy_data: PrivacySettingsUpdate) -> User:
        """Update user privacy settings"""
        user = self.get_user_profile(user_id)

        # Update only fields that are provided
        update_dict = privacy_data.model_dump(exclude_unset=True)

        if not update_dict:
            return user

        updated_user = self.profile_repo.update_privacy_settings(
            user=user,
            data_sharing_consent=update_dict.get("data_sharing_consent"),
            analytics_consent=update_dict.get("analytics_consent")
        )

        return updated_user

    def get_profile_initials(self, user: User) -> str:
        """Generate initials from user's name for avatar display"""
        if user.full_name:
            names = user.full_name.split()
            if len(names) >= 2:
                return f"{names[0][0]}{names[-1][0]}".upper()
            elif len(names) == 1:
                return names[0][:2].upper()

        # Fallback to username
        return user.username[:2].upper()

    def delete_avatar(self, user_id: int) -> User:
        """Remove user's avatar"""
        user = self.get_user_profile(user_id)
        user.avatar_url = None
        self.db.commit()
        self.db.refresh(user)
        return user
