from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ListingMediaType
from app.models.mixins import TimestampMixin


class PropertyListingMedia(Base, TimestampMixin):
    __tablename__ = "property_listing_media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("property_listings.id"), nullable=False, index=True)
    media_type: Mapped[ListingMediaType] = mapped_column(
        Enum(ListingMediaType, name="listing_media_type"),
        nullable=False,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    listing: Mapped["PropertyListing"] = relationship(back_populates="media_items")


from app.models.property_listing import PropertyListing  # noqa: E402,F401
