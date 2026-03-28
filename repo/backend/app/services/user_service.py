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
    def create_user(
        db: Session,
        username: str,
        password: str,
        role: UserRole,
        shipping_address: str | None = None,
        mailing_address: str | None = None,
    ) -> User:
        user = User(
            username=username,
            password=hash_password(password),
            role=role,
            shipping_address=shipping_address,
            mailing_address=mailing_address,
        )
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

    @staticmethod
    def update_user_address(
        db: Session,
        user_id: int,
        shipping_address: str | None,
        mailing_address: str | None,
    ) -> User | None:
        user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        if not user:
            return None

        user.shipping_address = shipping_address
        user.mailing_address = mailing_address
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
