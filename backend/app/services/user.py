"""User service."""

from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, User


class UserService:
    """User management service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        # TODO: Implement database query
        return None
    
    def get_user_by_username(self, username: str) -> User | None:
        """Get user by username."""
        # TODO: Implement database query
        return None
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create new user."""
        # TODO: Implement user creation logic
        from datetime import datetime
        return User(
            id=1,
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            is_active=user_data.is_active,
            created_at=datetime.now()
        )