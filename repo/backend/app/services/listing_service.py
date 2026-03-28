from decimal import Decimal
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_logger, settings
from app.models.enums import ListingMediaType, ListingStatus, UserRole
from app.models.property_listing import PropertyListing
from app.models.property_listing_media import PropertyListingMedia
from app.models.user import User
from app.services.file_validation import (
    build_storage_filename,
    ensure_upload_directory,
    validate_upload_file,
)

logger = get_logger(__name__)


class ListingService:
    @staticmethod
    def _base_query() -> Select:
        return select(PropertyListing).options(joinedload(PropertyListing.media_items))

    @staticmethod
    def _validate_listing_fields(title: str | None, description: str | None) -> None:
        if title is not None and len(title.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Title must be at least 3 characters",
            )
        if description is not None and len(description.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Description must be at least 3 characters",
            )

    @staticmethod
    def create_listing(
        db: Session,
        owner_user_id: int,
        title: str,
        description: str,
        price_amount: Decimal | None,
        listing_status: ListingStatus,
        files: list[UploadFile],
    ) -> PropertyListing:
        ListingService._validate_listing_fields(title=title, description=description)

        listing = PropertyListing(
            owner_user_id=owner_user_id,
            title=title.strip(),
            description=description.strip(),
            price_amount=price_amount,
            status=listing_status,
        )

        try:
            db.add(listing)
            db.flush()
            ListingService._save_media_files(db, listing.id, files)
            db.commit()
            logger.info(
                "Listing created listing_id=%s owner_user_id=%s status=%s",
                listing.id,
                owner_user_id,
                listing_status.value,
            )
        except HTTPException:
            db.rollback()
            logger.warning(
                "Listing create validation failure owner_user_id=%s title=%s",
                owner_user_id,
                title,
                exc_info=True,
            )
            raise
        except SQLAlchemyError:
            db.rollback()
            logger.error(
                "Listing create database error owner_user_id=%s title=%s",
                owner_user_id,
                title,
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create listing",
            )

        return ListingService.get_by_id_or_404(db, listing.id)

    @staticmethod
    def update_listing(
        db: Session,
        listing_id: int,
        title: str | None,
        description: str | None,
        price_amount: Decimal | None,
        listing_status: ListingStatus | None,
        files: list[UploadFile],
    ) -> PropertyListing:
        ListingService._validate_listing_fields(title=title, description=description)
        listing = ListingService.get_by_id_or_404(db, listing_id)

        if title is not None:
            listing.title = title.strip()
        if description is not None:
            listing.description = description.strip()
        if price_amount is not None:
            listing.price_amount = price_amount
        if listing_status is not None:
            listing.status = listing_status

        try:
            ListingService._save_media_files(db, listing.id, files)
            db.add(listing)
            db.commit()
            logger.info("Listing updated listing_id=%s status=%s", listing.id, listing.status.value)
        except HTTPException:
            db.rollback()
            logger.warning("Listing update validation failure listing_id=%s", listing_id, exc_info=True)
            raise
        except SQLAlchemyError:
            db.rollback()
            logger.error("Listing update database error listing_id=%s", listing_id, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update listing",
            )

        return ListingService.get_by_id_or_404(db, listing.id)

    @staticmethod
    def get_listings(
        db: Session,
        listing_status: ListingStatus | None,
        owner_user_id: int | None,
    ) -> list[PropertyListing]:
        query = ListingService._base_query()

        if listing_status is not None:
            query = query.where(PropertyListing.status == listing_status)
        if owner_user_id is not None:
            query = query.where(PropertyListing.owner_user_id == owner_user_id)

        return list(db.execute(query.order_by(PropertyListing.created_at.desc())).scalars().unique().all())

    @staticmethod
    def publish_listing(db: Session, listing_id: int, user_id: int) -> PropertyListing:
        listing = ListingService.get_by_id_or_404(db, listing_id)
        user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        if user is None:
            logger.warning("Listing publish failed: user not found listing_id=%s user_id=%s", listing_id, user_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user.role != UserRole.manager and listing.owner_user_id != user.id:
            logger.warning(
                "Listing publish forbidden listing_id=%s user_id=%s owner_user_id=%s",
                listing_id,
                user_id,
                listing.owner_user_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to publish this listing",
            )

        listing.status = ListingStatus.published
        try:
            db.add(listing)
            db.commit()
            logger.info("Listing published listing_id=%s by_user_id=%s", listing_id, user_id)
        except SQLAlchemyError:
            db.rollback()
            logger.error("Listing publish database error listing_id=%s user_id=%s", listing_id, user_id, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to publish listing",
            )

        return ListingService.get_by_id_or_404(db, listing.id)

    @staticmethod
    def bulk_update_status(db: Session, listing_ids: list[int], listing_status: ListingStatus) -> int:
        listings = db.execute(
            ListingService._base_query().where(PropertyListing.id.in_(listing_ids))
        ).scalars().unique().all()

        if len(listings) != len(listing_ids):
            logger.warning("Bulk listing status update failed: listing(s) missing ids=%s", listing_ids)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more listings were not found",
            )

        try:
            for listing in listings:
                listing.status = listing_status
                db.add(listing)

            db.commit()
            logger.info(
                "Bulk listing status update applied count=%s status=%s ids=%s",
                len(listings),
                listing_status.value,
                listing_ids,
            )
        except SQLAlchemyError:
            db.rollback()
            logger.error(
                "Bulk listing status update database error status=%s ids=%s",
                listing_status.value,
                listing_ids,
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update listing statuses",
            )

        return len(listings)

    @staticmethod
    def get_by_id_or_404(db: Session, listing_id: int) -> PropertyListing:
        listing = db.execute(
            ListingService._base_query().where(PropertyListing.id == listing_id)
        ).scalars().unique().one_or_none()

        if listing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

        return listing

    @staticmethod
    def validate_media(files: list[UploadFile]) -> list[tuple[UploadFile, bytes, int, ListingMediaType]]:
        prepared_files: list[tuple[UploadFile, bytes, int, ListingMediaType]] = []
        for upload in files:
            file_bytes = upload.file.read()
            file_size = len(file_bytes)
            media_type = validate_upload_file(upload, file_size)
            prepared_files.append((upload, file_bytes, file_size, media_type))
        return prepared_files

    @staticmethod
    def _save_media_files(db: Session, listing_id: int, files: list[UploadFile]) -> None:
        if not files:
            return

        upload_dir = ensure_upload_directory()
        prepared_files = ListingService.validate_media(files)

        for upload, file_bytes, file_size, media_type in prepared_files:
            stored_name = build_storage_filename(upload.filename)
            stored_path = upload_dir / stored_name
            stored_path.write_bytes(file_bytes)

            media = PropertyListingMedia(
                listing_id=listing_id,
                media_type=media_type,
                file_name=upload.filename or stored_name,
                file_path=str(Path(settings.listing_upload_dir) / stored_name),
                mime_type=upload.content_type or "application/octet-stream",
                file_size_bytes=file_size,
            )
            db.add(media)
