from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ..dependencies import get_current_user_id
from ...schemas.artwork import (
    ArtworkCreate,
    ArtworkUpdate,
    ArtworkResponse,
    ArtworkListResponse,
    ArtworkThumbnailResponse,
)
from ...services.artwork_service import ArtworkService

router = APIRouter(prefix="/api/artworks", tags=["artworks"])


@router.post("/", response_model=ArtworkResponse, status_code=status.HTTP_201_CREATED)
async def create_artwork(
    artwork_data: ArtworkCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create a new artwork"""
    service = ArtworkService(db)
    artwork = service.create_artwork(user_id, artwork_data)
    return artwork


@router.get("/", response_model=ArtworkListResponse)
async def get_user_artworks(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of items to return"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get all artworks for the current user"""
    service = ArtworkService(db)
    artworks, total = service.get_user_artworks(user_id, skip, limit)
    return {"artworks": artworks, "total": total}


@router.get("/thumbnails", response_model=List[ArtworkThumbnailResponse])
async def get_artwork_thumbnails(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get artwork thumbnails for gallery view"""
    service = ArtworkService(db)
    artworks, _ = service.get_user_artworks(user_id, skip, limit)

    # Return only thumbnail data for efficient loading
    return [
        {
            "id": artwork.id,
            "title": artwork.title,
            "thumbnail_data": artwork.thumbnail_data or artwork.image_data,
            "created_at": artwork.created_at,
        }
        for artwork in artworks
    ]


@router.get("/{artwork_id}", response_model=ArtworkResponse)
async def get_artwork(
    artwork_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get a specific artwork by ID"""
    service = ArtworkService(db)
    artwork = service.get_artwork(artwork_id, user_id)

    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artwork not found",
        )

    return artwork


@router.put("/{artwork_id}", response_model=ArtworkResponse)
async def update_artwork(
    artwork_id: int,
    artwork_data: ArtworkUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Update artwork (only title)"""
    service = ArtworkService(db)
    artwork = service.update_artwork(artwork_id, user_id, artwork_data)

    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artwork not found",
        )

    return artwork


@router.delete("/{artwork_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artwork(
    artwork_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete an artwork"""
    service = ArtworkService(db)
    success = service.delete_artwork(artwork_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artwork not found",
        )

    return None
