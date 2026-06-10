from sqlalchemy.orm import Session
from typing import List, Optional
from ..repositories.artwork_repo import ArtworkRepository
from ..schemas.artwork import ArtworkCreate, ArtworkUpdate, ArtworkResponse, ArtworkThumbnailResponse
from ..models.artwork import Artwork


class ArtworkService:
    """Service layer for artwork business logic"""

    def __init__(self, db: Session):
        self.repo = ArtworkRepository(db)

    def create_artwork(self, user_id: int, artwork_data: ArtworkCreate) -> Artwork:
        """Create a new artwork"""
        return self.repo.create(user_id, artwork_data)

    def get_artwork(self, artwork_id: int, user_id: int) -> Optional[Artwork]:
        """Get artwork by ID"""
        return self.repo.get_by_id(artwork_id, user_id)

    def get_user_artworks(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[List[Artwork], int]:
        """Get all artworks for a user with total count"""
        artworks = self.repo.get_user_artworks(user_id, skip, limit)
        total = self.repo.get_user_artworks_count(user_id)
        return artworks, total

    def update_artwork(
        self, artwork_id: int, user_id: int, artwork_data: ArtworkUpdate
    ) -> Optional[Artwork]:
        """Update artwork"""
        return self.repo.update(artwork_id, user_id, artwork_data)

    def delete_artwork(self, artwork_id: int, user_id: int) -> bool:
        """Delete artwork"""
        return self.repo.delete(artwork_id, user_id)
