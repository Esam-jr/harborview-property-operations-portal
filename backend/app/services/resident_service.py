from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.user import User
from app.services.user_service import UserService


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

        try:
            updated = UserService.update_user_address(
                db=db,
                user_id=current_user.id,
                shipping_address=shipping_address,
                mailing_address=mailing_address,
            )
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update resident addresses",
            )

        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

        return updated

    @staticmethod
    def _require_resident(current_user: User) -> None:
        if current_user.role != UserRole.resident:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Resident role required",
            )
