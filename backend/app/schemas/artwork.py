from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ArtworkCreate(BaseModel):
    """Schema for creating artwork"""
    title: Optional[str] = Field(None, max_length=255, description="Optional title for the artwork")
    image_data: str = Field(..., description="Base64 encoded PNG image data")
    thumbnail_data: Optional[str] = Field(None, description="Base64 encoded thumbnail")


class ArtworkUpdate(BaseModel):
    """Schema for updating artwork"""
    title: Optional[str] = Field(None, max_length=255)


class ArtworkResponse(BaseModel):
    """Schema for artwork response"""
    id: int
    user_id: int
    title: Optional[str]
    image_data: str
    thumbnail_data: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArtworkListResponse(BaseModel):
    """Schema for list of artworks"""
    artworks: list[ArtworkResponse]
    total: int


class ArtworkThumbnailResponse(BaseModel):
    """Schema for artwork thumbnail (for gallery view)"""
    id: int
    title: Optional[str]
    thumbnail_data: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
