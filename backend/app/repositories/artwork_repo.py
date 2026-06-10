from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.artwork import Artwork
from ..schemas.artwork import ArtworkCreate, ArtworkUpdate


class ArtworkRepository:
    """Repository for artwork database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, artwork_data: ArtworkCreate) -> Artwork:
        """Create a new artwork"""
        artwork = Artwork(
            user_id=user_id,
            title=artwork_data.title,
            image_data=artwork_data.image_data,
            thumbnail_data=artwork_data.thumbnail_data,
        )
        self.db.add(artwork)
        self.db.commit()
        self.db.refresh(artwork)
        return artwork

    def get_by_id(self, artwork_id: int, user_id: int) -> Optional[Artwork]:
        """Get artwork by ID (only if it belongs to the user)"""
        return (
            self.db.query(Artwork)
            .filter(Artwork.id == artwork_id, Artwork.user_id == user_id)
            .first()
        )

    def get_user_artworks(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Artwork]:
        """Get all artworks for a user"""
        return (
            self.db.query(Artwork)
            .filter(Artwork.user_id == user_id)
            .order_by(Artwork.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_artworks_count(self, user_id: int) -> int:
        """Get total count of artworks for a user"""
        return self.db.query(Artwork).filter(Artwork.user_id == user_id).count()

    def update(
        self, artwork_id: int, user_id: int, artwork_data: ArtworkUpdate
    ) -> Optional[Artwork]:
        """Update artwork (only title for now)"""
        artwork = self.get_by_id(artwork_id, user_id)
        if not artwork:
            return None

        if artwork_data.title is not None:
            artwork.title = artwork_data.title

        self.db.commit()
        self.db.refresh(artwork)
        return artwork

    def delete(self, artwork_id: int, user_id: int) -> bool:
        """Delete artwork"""
        artwork = self.get_by_id(artwork_id, user_id)
        if not artwork:
            return False

        self.db.delete(artwork)
        self.db.commit()
        return True
