from sqlalchemy.orm import Session
from typing import Optional
from ..repositories.user_repo import UserRepository
from ..core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from ..schemas.user import UserCreate, UserLogin, TokenResponse
from fastapi import HTTPException, status


class UserService:
    """Service layer for user-related business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, user_data: UserCreate) -> dict:
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

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "message": "User registered successfully"
        }

    def authenticate_user(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return tokens"""
        user = self.user_repo.get_by_email(login_data.email)

        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        # Create tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def get_user_by_id(self, user_id: int):
        """Get user by ID"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def update_user_profile(self, user_id: int, full_name: Optional[str] = None, email: Optional[str] = None):
        """Update user profile"""
        user = self.get_user_by_id(user_id)

        if email and email != user.email:
            if self.user_repo.get_by_email(email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            user.email = email

        if full_name:
            user.full_name = full_name

        return self.user_repo.update(user)
