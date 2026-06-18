from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...schemas.profile import (
    ProfileResponse,
    ProfileUpdate,
    PreferencesUpdate,
    PrivacySettingsUpdate,
    ProfilePreferences,
    ProfilePrivacySettings
)
from ...services.profile_service import ProfileService
from ...models.user import User
from ..dependencies import get_current_user

router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user's complete profile.

    Endpoint: GET /api/profile/me

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - ProfileResponse with complete user profile including preferences and privacy settings
    """
    profile_service = ProfileService(db)
    user = profile_service.get_user_profile(current_user.id)
    return ProfileResponse.model_validate(user)


@router.put("/me", response_model=ProfileResponse)
def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information.

    Endpoint: PUT /api/profile/me

    Headers:
    - Authorization: Bearer <access_token>

    Request body:
    - full_name: Optional full name
    - phone_number: Optional phone number
    - bio: Optional biography
    - avatar_url: Optional avatar URL

    Returns:
    - Updated ProfileResponse
    """
    profile_service = ProfileService(db)
    updated_user = profile_service.update_profile(current_user.id, profile_data)
    return ProfileResponse.model_validate(updated_user)


@router.get("/me/preferences", response_model=ProfilePreferences)
def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's notification preferences.

    Endpoint: GET /api/profile/me/preferences

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - ProfilePreferences with notification settings
    """
    profile_service = ProfileService(db)
    user = profile_service.get_user_profile(current_user.id)
    return ProfilePreferences(
        notifications_enabled=user.notifications_enabled,
        email_notifications=user.email_notifications
    )


@router.put("/me/preferences", response_model=ProfileResponse)
def update_my_preferences(
    preferences_data: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's notification preferences.

    Endpoint: PUT /api/profile/me/preferences

    Headers:
    - Authorization: Bearer <access_token>

    Request body:
    - notifications_enabled: Optional boolean for push notifications
    - email_notifications: Optional boolean for email notifications

    Returns:
    - Updated ProfileResponse
    """
    profile_service = ProfileService(db)
    updated_user = profile_service.update_preferences(current_user.id, preferences_data)
    return ProfileResponse.model_validate(updated_user)


@router.get("/me/privacy", response_model=ProfilePrivacySettings)
def get_my_privacy_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's privacy settings.

    Endpoint: GET /api/profile/me/privacy

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - ProfilePrivacySettings with privacy configurations
    """
    profile_service = ProfileService(db)
    user = profile_service.get_user_profile(current_user.id)
    return ProfilePrivacySettings(
        data_sharing_consent=user.data_sharing_consent,
        analytics_consent=user.analytics_consent
    )


@router.put("/me/privacy", response_model=ProfileResponse)
def update_my_privacy_settings(
    privacy_data: PrivacySettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's privacy settings.

    Endpoint: PUT /api/profile/me/privacy

    Headers:
    - Authorization: Bearer <access_token>

    Request body:
    - data_sharing_consent: Optional boolean for data sharing consent
    - analytics_consent: Optional boolean for analytics consent

    Returns:
    - Updated ProfileResponse
    """
    profile_service = ProfileService(db)
    updated_user = profile_service.update_privacy_settings(current_user.id, privacy_data)
    return ProfileResponse.model_validate(updated_user)


@router.delete("/me/avatar", response_model=ProfileResponse)
def delete_my_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove current user's avatar.

    Endpoint: DELETE /api/profile/me/avatar

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - Updated ProfileResponse with avatar_url set to null
    """
    profile_service = ProfileService(db)
    updated_user = profile_service.delete_avatar(current_user.id)
    return ProfileResponse.model_validate(updated_user)


@router.get("/me/initials")
def get_my_initials(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's initials for avatar display.

    Endpoint: GET /api/profile/me/initials

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - JSON with initials string
    """
    profile_service = ProfileService(db)
    initials = profile_service.get_profile_initials(current_user)
    return {"initials": initials}
