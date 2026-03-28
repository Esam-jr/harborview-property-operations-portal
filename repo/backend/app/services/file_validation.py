from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.models.enums import ListingMediaType


def ensure_upload_directory() -> Path:
    upload_dir = Path(settings.listing_upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def _resolve_media_type(content_type: str) -> ListingMediaType:
    if content_type in settings.allowed_image_types:
        return ListingMediaType.image
    if content_type in settings.allowed_video_types:
        return ListingMediaType.video
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported file format. Allowed: JPG, PNG, MP4",
    )


def validate_upload_file(upload: UploadFile, file_size: int) -> ListingMediaType:
    if not upload.content_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File content type is missing")

    media_type = _resolve_media_type(upload.content_type)

    if media_type == ListingMediaType.image and file_size > settings.listing_max_image_size_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image exceeds 10MB limit")

    if media_type == ListingMediaType.video and file_size > settings.listing_max_video_size_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Video exceeds 200MB limit")

    return media_type


def build_storage_filename(original_filename: str | None) -> str:
    suffix = Path(original_filename).suffix if original_filename else ""
    return f"{uuid4().hex}{suffix.lower()}"
