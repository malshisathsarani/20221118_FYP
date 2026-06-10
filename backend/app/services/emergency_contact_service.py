from sqlalchemy.orm import Session
from typing import List
from ..repositories.emergency_contact_repo import EmergencyContactRepository
from ..schemas.emergency_contact import EmergencyContactCreate, EmergencyContactUpdate
from ..models.emergency_contact import EmergencyContact
from fastapi import HTTPException, status


class EmergencyContactService:
    """Service layer for emergency contact operations"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = EmergencyContactRepository(db)

    def create_contact(self, user_id: int, contact_data: EmergencyContactCreate) -> EmergencyContact:
        """Create a new emergency contact for a user"""
        return self.repo.create(
            user_id=user_id,
            name=contact_data.name,
            phone=contact_data.phone,
            relationship_type=contact_data.relationship_type,
            email=contact_data.email,
            is_primary=contact_data.is_primary
        )

    def get_user_contacts(self, user_id: int) -> List[EmergencyContact]:
        """Get all emergency contacts for a user"""
        return self.repo.get_user_contacts(user_id)

    def get_contact(self, contact_id: int, user_id: int) -> EmergencyContact:
        """Get a specific emergency contact"""
        contact = self.repo.get_by_id(contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency contact not found"
            )
        if contact.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this contact"
            )
        return contact

    def update_contact(self, contact_id: int, user_id: int,
                      update_data: EmergencyContactUpdate) -> EmergencyContact:
        """Update an emergency contact"""
        contact = self.get_contact(contact_id, user_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        updated_contact = self.repo.update(contact_id, **update_dict)

        if not updated_contact:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update contact"
            )
        return updated_contact

    def delete_contact(self, contact_id: int, user_id: int) -> bool:
        """Delete an emergency contact"""
        contact = self.get_contact(contact_id, user_id)
        return self.repo.delete(contact_id)

    def set_primary_contact(self, contact_id: int, user_id: int) -> EmergencyContact:
        """Set a contact as the primary emergency contact"""
        contact = self.get_contact(contact_id, user_id)
        updated_contact = self.repo.set_primary(contact_id, user_id)
        if not updated_contact:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to set primary contact"
            )
        return updated_contact
