from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ProfilePreferences(BaseModel):
    """User notification preferences"""
    notifications_enabled: bool = True
    email_notifications: bool = True


class ProfilePrivacySettings(BaseModel):
    """User privacy settings"""
    data_sharing_consent: bool = False
    analytics_consent: bool = False


class ProfileUpdate(BaseModel):
    """Schema for updating profile information"""
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class PreferencesUpdate(BaseModel):
    """Schema for updating preferences"""
    notifications_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None


class PrivacySettingsUpdate(BaseModel):
    """Schema for updating privacy settings"""
    data_sharing_consent: Optional[bool] = None
    analytics_consent: Optional[bool] = None


class ProfileResponse(BaseModel):
    """Complete profile response"""
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    # Preferences
    notifications_enabled: bool
    email_notifications: bool

    # Privacy settings
    data_sharing_consent: bool
    analytics_consent: bool

    class Config:
        from_attributes = True
