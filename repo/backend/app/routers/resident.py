from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.resident import ResidentAddressUpdate, ResidentProfileRead
from app.services.resident_service import ResidentService

router = APIRouter(prefix="/resident", tags=["resident"])


@router.get("/profile", response_model=ResidentProfileRead)
def get_resident_profile(
    current_user: User = Depends(get_current_user),
) -> ResidentProfileRead:
    if current_user.role != UserRole.resident:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Resident role required",
        )

    resident = ResidentService.get_profile(current_user)
    return ResidentProfileRead(
        id=resident.id,
        username=resident.username,
        role=resident.role,
        shipping_address=resident.shipping_address,
        mailing_address=resident.mailing_address,
    )


@router.put("/address", response_model=ResidentProfileRead)
def update_resident_address(
    payload: ResidentAddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResidentProfileRead:
    if current_user.role != UserRole.resident:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Resident role required",
        )

    resident = ResidentService.update_addresses(
        db=db,
        current_user=current_user,
        shipping_address=payload.shipping_address,
        mailing_address=payload.mailing_address,
    )
    return ResidentProfileRead(
        id=resident.id,
        username=resident.username,
        role=resident.role,
        shipping_address=resident.shipping_address,
        mailing_address=resident.mailing_address,
    )
