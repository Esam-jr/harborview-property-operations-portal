from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.enums import UserRole
from app.models.user import User


class UserService:
    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        return db.execute(select(User).where(User.username == username)).scalar_one_or_none()

    @staticmethod
    def create_user(db: Session, username: str, password: str, role: UserRole) -> User:
        user = User(username=username, password=hash_password(password), role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> User | None:
        user = UserService.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
