from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


def ensure_billing_proof_upload_directory() -> Path:
    upload_dir = Path(settings.billing_proof_upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def validate_billing_proof_file(upload: UploadFile, file_size: int) -> None:
    if not upload.content_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File content type is missing")

    if upload.content_type not in settings.billing_allowed_proof_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported proof format. Allowed: JPG, PNG",
        )

    if file_size > settings.billing_max_image_size_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Proof image exceeds 10MB limit")


def build_proof_storage_filename(original_filename: str | None) -> str:
    suffix = Path(original_filename).suffix if original_filename else ""
    return f"{uuid4().hex}{suffix.lower()}"
