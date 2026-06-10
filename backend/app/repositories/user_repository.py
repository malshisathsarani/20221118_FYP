from sqlalchemy.orm import Session
from typing import Optional
from ..models.user import User


class UserRepository:
    """Repository for User database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, username: str, hashed_password: str, full_name: Optional[str] = None) -> User:
        """Create a new user"""
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    def update(self, user: User) -> User:
        """Update user"""
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        """Delete user"""
        self.db.delete(user)
        self.db.commit()

    def verify_user(self, user: User) -> User:
        """Mark user as verified"""
        user.is_verified = True
        return self.update(user)

    def deactivate_user(self, user: User) -> User:
        """Deactivate user"""
        user.is_active = False
        return self.update(user)
