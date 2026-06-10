from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class EmergencyContactCreate(BaseModel):
    """Schema for creating an emergency contact"""
    name: str
    phone: str
    relationship_type: Optional[str] = None
    email: Optional[EmailStr] = None
    is_primary: Optional[int] = 0


class EmergencyContactUpdate(BaseModel):
    """Schema for updating an emergency contact"""
    name: Optional[str] = None
    phone: Optional[str] = None
    relationship_type: Optional[str] = None
    email: Optional[EmailStr] = None
    is_primary: Optional[int] = None


class EmergencyContactResponse(BaseModel):
    """Schema for emergency contact response"""
    id: int
    user_id: int
    name: str
    phone: str
    relationship_type: Optional[str] = None
    email: Optional[str] = None
    is_primary: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmergencyContactListResponse(BaseModel):
    """Schema for list of emergency contacts"""
    contacts: list[EmergencyContactResponse]
    total: int
