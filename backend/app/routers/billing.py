from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import PaymentMethod, StatementFormat, UserRole
from app.models.user import User
from app.schemas.billing import (
    BillingCreate,
    BillingRead,
    RefundRequest,
    RefundResponse,
    UploadProofResponse,
)
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("", response_model=BillingRead, status_code=status.HTTP_201_CREATED)
def create_billing_record(
    payload: BillingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BillingRead:
    if current_user.role not in {UserRole.admin, UserRole.manager, UserRole.clerk}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, manager, or clerk can create billing records",
        )

    record = BillingService.create_billing_record(
        db=db,
        resident_user_id=payload.resident_user_id,
        amount_due=payload.amount_due,
        due_date=payload.due_date,
        notes=payload.notes,
    )
    return BillingRead.model_validate(record)


@router.get("", response_model=list[BillingRead])
def get_billing_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BillingRead]:
    records = BillingService.get_billing_records(db=db, current_user=current_user)
    return [BillingRead.model_validate(record) for record in records]


@router.get("/{billing_id}/statement")
def download_statement(
    billing_id: int,
    format: StatementFormat = StatementFormat.json,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = BillingService.download_statement(
        db=db,
        billing_id=billing_id,
        current_user=current_user,
        fmt=format,
    )
    if isinstance(result, Response):
        return result
    return result


@router.post("/{billing_id}/upload-proof", response_model=UploadProofResponse)
def upload_payment_proof(
    billing_id: int,
    payment_method: PaymentMethod = Form(...),
    amount: Decimal = Form(...),
    payment_date: date = Form(...),
    reference_number: str | None = Form(default=None),
    proof_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UploadProofResponse:
    evidence = BillingService.upload_payment_proof(
        db=db,
        billing_id=billing_id,
        current_user=current_user,
        payment_method=payment_method,
        amount=amount,
        payment_date=payment_date,
        reference_number=reference_number,
        proof_file=proof_file,
    )

    return UploadProofResponse(
        evidence_id=evidence.id,
        billing_id=evidence.billing_record_id,
        file_name=evidence.file_name,
        file_mime_type=evidence.file_mime_type,
        file_size_bytes=evidence.file_size_bytes,
        payment_method=evidence.payment_method,
    )


@router.post("/{billing_id}/refund", response_model=RefundResponse)
def request_refund(
    billing_id: int,
    payload: RefundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RefundResponse:
    record = BillingService.request_refund(
        db=db,
        billing_id=billing_id,
        current_user=current_user,
        amount=payload.amount,
        reason=payload.reason,
    )

    return RefundResponse(
        billing_id=record.id,
        credit_amount=payload.amount,
        status=record.status,
        message="Refund requested as resident credit",
    )
