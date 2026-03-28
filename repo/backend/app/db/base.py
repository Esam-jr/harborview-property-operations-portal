from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models so SQLAlchemy metadata is registered before create_all.
from app.models import (  # noqa: E402,F401
    BillingRecord,
    HomePageConfig,
    PaymentEvidence,
    PropertyListing,
    PropertyListingMedia,
    ServiceOrder,
    ServiceOrderStatusHistory,
    User,
)
