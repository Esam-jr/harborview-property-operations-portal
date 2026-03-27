from decimal import Decimal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import ListingStatus, UserRole
from app.models.user import User
from app.schemas.listing import (
    ListingBulkUpdateRequest,
    ListingBulkUpdateResponse,
    ListingRead,
)
from app.services.listing_service import ListingService

router = APIRouter(prefix="/listings", tags=["listings"])


def _require_manager(user: User) -> None:
    if user.role != UserRole.manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only manager role can manage listings",
        )


@router.post("", response_model=ListingRead)
def create_listing(
    title: str = Form(...),
    description: str = Form(...),
    listing_status: ListingStatus = Form(default=ListingStatus.draft, alias="status"),
    price_amount: Decimal | None = Form(default=None),
    files: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ListingRead:
    _require_manager(current_user)

    listing = ListingService.create_listing(
        db=db,
        owner_user_id=current_user.id,
        title=title,
        description=description,
        price_amount=price_amount,
        listing_status=listing_status,
        files=files,
    )
    return ListingRead.model_validate(listing)


@router.put("/{listing_id}", response_model=ListingRead)
def edit_listing(
    listing_id: int,
    title: str | None = Form(default=None),
    description: str | None = Form(default=None),
    listing_status: ListingStatus | None = Form(default=None, alias="status"),
    price_amount: Decimal | None = Form(default=None),
    files: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ListingRead:
    _require_manager(current_user)

    if all(field is None for field in [title, description, price_amount, listing_status]) and len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field or media file must be provided",
        )

    listing = ListingService.update_listing(
        db=db,
        listing_id=listing_id,
        title=title,
        description=description,
        price_amount=price_amount,
        listing_status=listing_status,
        files=files,
    )
    return ListingRead.model_validate(listing)


@router.get("", response_model=list[ListingRead])
def get_listings(
    status: ListingStatus | None = None,
    owner_user_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[ListingRead]:
    listings = ListingService.get_listings(db=db, listing_status=status, owner_user_id=owner_user_id)
    return [ListingRead.model_validate(item) for item in listings]


@router.patch("/bulk-update", response_model=ListingBulkUpdateResponse)
def bulk_update_listings(
    payload: ListingBulkUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ListingBulkUpdateResponse:
    _require_manager(current_user)

    updated_count = ListingService.bulk_update_status(
        db=db,
        listing_ids=payload.ids,
        listing_status=payload.status,
    )
    return ListingBulkUpdateResponse(updated_count=updated_count, status=payload.status)
