from decimal import Decimal
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.enums import ListingMediaType, ListingStatus, UserRole
from app.models.property_listing import PropertyListing
from app.models.property_listing_media import PropertyListingMedia
from app.models.user import User
from app.services.file_validation import (
    build_storage_filename,
    ensure_upload_directory,
    validate_upload_file,
)


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
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError:
            db.rollback()
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
        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError:
            db.rollback()
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user.role != UserRole.manager and listing.owner_user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to publish this listing",
            )

        listing.status = ListingStatus.published
        try:
            db.add(listing)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more listings were not found",
            )

        try:
            for listing in listings:
                listing.status = listing_status
                db.add(listing)

            db.commit()
        except SQLAlchemyError:
            db.rollback()
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
