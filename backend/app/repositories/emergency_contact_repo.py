from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.emergency_contact import EmergencyContact


class EmergencyContactRepository:
    """Repository for emergency contact database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, name: str, phone: str,
               relationship_type: Optional[str] = None,
               email: Optional[str] = None,
               is_primary: int = 0) -> EmergencyContact:
        """Create a new emergency contact"""
        contact = EmergencyContact(
            user_id=user_id,
            name=name,
            phone=phone,
            relationship_type=relationship_type,
            email=email,
            is_primary=is_primary
        )
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def get_by_id(self, contact_id: int) -> Optional[EmergencyContact]:
        """Get emergency contact by ID"""
        return self.db.query(EmergencyContact).filter(
            EmergencyContact.id == contact_id
        ).first()

    def get_user_contacts(self, user_id: int) -> List[EmergencyContact]:
        """Get all emergency contacts for a user"""
        return self.db.query(EmergencyContact).filter(
            EmergencyContact.user_id == user_id
        ).order_by(EmergencyContact.is_primary.desc(), EmergencyContact.created_at.desc()).all()

    def get_primary_contact(self, user_id: int) -> Optional[EmergencyContact]:
        """Get the primary emergency contact for a user"""
        return self.db.query(EmergencyContact).filter(
            EmergencyContact.user_id == user_id,
            EmergencyContact.is_primary == 1
        ).first()

    def update(self, contact_id: int, **kwargs) -> Optional[EmergencyContact]:
        """Update an emergency contact"""
        contact = self.get_by_id(contact_id)
        if contact:
            for key, value in kwargs.items():
                if value is not None and hasattr(contact, key):
                    setattr(contact, key, value)
            self.db.commit()
            self.db.refresh(contact)
        return contact

    def delete(self, contact_id: int) -> bool:
        """Delete an emergency contact"""
        contact = self.get_by_id(contact_id)
        if contact:
            self.db.delete(contact)
            self.db.commit()
            return True
        return False

    def set_primary(self, contact_id: int, user_id: int) -> Optional[EmergencyContact]:
        """Set a contact as primary (and unset others)"""
        # First, unset all primary contacts for this user
        self.db.query(EmergencyContact).filter(
            EmergencyContact.user_id == user_id
        ).update({"is_primary": 0})

        # Then set the specified contact as primary
        contact = self.get_by_id(contact_id)
        if contact and contact.user_id == user_id:
            contact.is_primary = 1
            self.db.commit()
            self.db.refresh(contact)
            return contact
        return None
