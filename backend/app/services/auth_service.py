from sqlalchemy.orm import Session
from typing import Optional
from ..repositories.user_repository import UserRepository
from ..core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from ..schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from ..models.user import User
from fastapi import HTTPException, status


class AuthService:
    """Service layer for authentication business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        # Check if email already exists
        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Check if username already exists
        if self.user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Hash password and create user
        hashed_password = get_password_hash(user_data.password)
        user = self.user_repo.create(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )

        return UserResponse.from_orm(user)

    def login(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return JWT tokens"""
        user = self.user_repo.get_by_email(login_data.email)

        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        # Create JWT tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    def get_current_user(self, user_id: int) -> User:
        """Get current authenticated user by ID"""
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )

        return user

    def verify_user_account(self, user_id: int) -> UserResponse:
        """Verify user account (email verification)"""
        user = self.get_current_user(user_id)
        verified_user = self.user_repo.verify_user(user)
        return UserResponse.from_orm(verified_user)

    def deactivate_account(self, user_id: int) -> UserResponse:
        """Deactivate user account"""
        user = self.get_current_user(user_id)
        deactivated_user = self.user_repo.deactivate_user(user)
        return UserResponse.from_orm(deactivated_user)

    def refresh_access_token(self, user_id: int, email: str) -> TokenResponse:
        """Generate new access token using refresh token"""
        user = self.get_current_user(user_id)

        if user.email != email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data"
            )

        # Create new tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
