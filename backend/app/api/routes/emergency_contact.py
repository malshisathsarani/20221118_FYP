from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...schemas.emergency_contact import (
    EmergencyContactCreate,
    EmergencyContactUpdate,
    EmergencyContactResponse,
    EmergencyContactListResponse
)
from ...services.emergency_contact_service import EmergencyContactService
from ..dependencies import get_current_user_id

router = APIRouter()


@router.post("/", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
def create_emergency_contact(
    contact: EmergencyContactCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new emergency contact.

    Endpoint: POST /api/emergency-contacts/

    Headers:
    - Authorization: Bearer <access_token>

    Request Body:
    - name: Contact's name
    - phone: Contact's phone number
    - relationship_type: Optional - e.g., "Family", "Friend", "Therapist"
    - email: Optional - Contact's email
    - is_primary: Optional - 0 (no) or 1 (yes), sets this as primary contact

    Returns:
    - Emergency contact details
    """
    service = EmergencyContactService(db)
    return service.create_contact(user_id, contact)


@router.get("/", response_model=EmergencyContactListResponse)
def get_emergency_contacts(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all emergency contacts for the current user.

    Endpoint: GET /api/emergency-contacts/

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - List of emergency contacts (ordered by primary first, then by creation date)
    """
    service = EmergencyContactService(db)
    contacts = service.get_user_contacts(user_id)
    return {
        "contacts": contacts,
        "total": len(contacts)
    }


@router.get("/{contact_id}", response_model=EmergencyContactResponse)
def get_emergency_contact(
    contact_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific emergency contact by ID.

    Endpoint: GET /api/emergency-contacts/{contact_id}

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - Emergency contact details
    """
    service = EmergencyContactService(db)
    return service.get_contact(contact_id, user_id)


@router.put("/{contact_id}", response_model=EmergencyContactResponse)
def update_emergency_contact(
    contact_id: int,
    contact_update: EmergencyContactUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update an emergency contact.

    Endpoint: PUT /api/emergency-contacts/{contact_id}

    Headers:
    - Authorization: Bearer <access_token>

    Request Body: (all fields optional)
    - name: Contact's name
    - phone: Contact's phone number
    - relationship_type: e.g., "Family", "Friend", "Therapist"
    - email: Contact's email
    - is_primary: 0 (no) or 1 (yes)

    Returns:
    - Updated emergency contact details
    """
    service = EmergencyContactService(db)
    return service.update_contact(contact_id, user_id, contact_update)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_emergency_contact(
    contact_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete an emergency contact.

    Endpoint: DELETE /api/emergency-contacts/{contact_id}

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - 204 No Content on success
    """
    service = EmergencyContactService(db)
    service.delete_contact(contact_id, user_id)
    return None


@router.patch("/{contact_id}/set-primary", response_model=EmergencyContactResponse)
def set_primary_emergency_contact(
    contact_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Set a contact as the primary emergency contact.
    This will unset any other primary contact for the user.

    Endpoint: PATCH /api/emergency-contacts/{contact_id}/set-primary

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - Updated emergency contact details
    """
    service = EmergencyContactService(db)
    return service.set_primary_contact(contact_id, user_id)
