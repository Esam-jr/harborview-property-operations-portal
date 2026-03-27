from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.models.enums import ListingStatus, UserRole
from app.services.listing_service import ListingService


def test_validate_listing_fields_rejects_short_title():
    with pytest.raises(HTTPException) as exc_info:
        ListingService._validate_listing_fields(title="ab", description="valid description")

    assert exc_info.value.status_code == 422
    assert "Title must be at least 3 characters" in str(exc_info.value.detail)


def test_create_listing_trims_fields_and_sets_status(db_session, create_user):
    owner = create_user("manager_owner", "owner-pass-123", UserRole.manager)

    listing = ListingService.create_listing(
        db=db_session,
        owner_user_id=owner.id,
        title="  Apartment 4B  ",
        description="  Recently renovated two-bedroom unit.  ",
        price_amount=Decimal("1300.00"),
        listing_status=ListingStatus.draft,
        files=[],
    )

    assert listing.id is not None
    assert listing.owner_user_id == owner.id
    assert listing.title == "Apartment 4B"
    assert listing.description == "Recently renovated two-bedroom unit."
    assert listing.status == ListingStatus.draft
