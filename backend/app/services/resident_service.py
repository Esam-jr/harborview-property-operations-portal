from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.user import User


class ResidentService:
    @staticmethod
    def get_profile(current_user: User) -> User:
        ResidentService._require_resident(current_user)
        return current_user

    @staticmethod
    def update_addresses(
        db: Session,
        current_user: User,
        shipping_address: str | None,
        mailing_address: str | None,
    ) -> User:
        ResidentService._require_resident(current_user)

        current_user.shipping_address = shipping_address
        current_user.mailing_address = mailing_address

        try:
            db.add(current_user)
            db.commit()
            db.refresh(current_user)
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update resident addresses",
            )

        return current_user

    @staticmethod
    def _require_resident(current_user: User) -> None:
        if current_user.role != UserRole.resident:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Resident role required",
            )
