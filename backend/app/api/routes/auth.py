from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from ...services.auth_service import AuthService
from ...models.user import User
from ..dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Endpoint: POST /api/auth/register

    Request body:
    - email: User's email address
    - username: Unique username
    - password: Password (min 8 characters)
    - full_name: Optional full name

    Returns:
    - UserResponse with user details (excluding password)
    """
    auth_service = AuthService(db)
    return auth_service.register(user_data)


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT tokens.

    Endpoint: POST /api/auth/login

    Request body:
    - email: User's email address
    - password: User's password

    Returns:
    - access_token: JWT access token (short-lived)
    - refresh_token: JWT refresh token (long-lived)
    - token_type: "bearer"
    """
    auth_service = AuthService(db)
    return auth_service.login(login_data)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.

    Endpoint: GET /api/auth/me

    Headers:
    - Authorization: Bearer <access_token>

    Returns:
    - UserResponse with current user details
    """
    return UserResponse.from_orm(current_user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    Endpoint: POST /api/auth/refresh

    Request body:
    - refresh_token: The refresh token

    Returns:
    - New access_token and refresh_token pair
    """
    from ...core.security import decode_token

    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = int(payload.get("sub"))
    email = payload.get("email")

    auth_service = AuthService(db)
    return auth_service.refresh_access_token(user_id, email)


@router.post("/verify/{user_id}", response_model=UserResponse)
def verify_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify user account (email verification).

    Endpoint: POST /api/auth/verify/{user_id}

    Note: In production, this should use a verification token sent via email.
    """
    # Only allow users to verify their own account
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to verify this account"
        )

    auth_service = AuthService(db)
    return auth_service.verify_user_account(user_id)


@router.post("/deactivate", response_model=UserResponse)
def deactivate_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate user account.

    Endpoint: POST /api/auth/deactivate

    Headers:
    - Authorization: Bearer <access_token>
    """
    auth_service = AuthService(db)
    return auth_service.deactivate_account(current_user.id)
