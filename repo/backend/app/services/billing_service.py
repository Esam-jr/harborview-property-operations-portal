from datetime import date
from decimal import Decimal

from fastapi import HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_logger
from app.models.billing_record import BillingRecord
from app.models.enums import BillingStatus, EvidenceType, PaymentMethod, StatementFormat, UserRole
from app.models.payment_evidence import PaymentEvidence
from app.models.user import User
from app.services.billing_file_validation import (
    build_proof_storage_filename,
    ensure_billing_proof_upload_directory,
    validate_billing_proof_file,
)
from app.services.utils import generate_reference

logger = get_logger(__name__)


class BillingService:
    @staticmethod
    def _base_query() -> Select:
        return select(BillingRecord).options(joinedload(BillingRecord.payment_evidences))

    @staticmethod
    def create_billing_record(
        db: Session,
        resident_user_id: int,
        amount_due: Decimal,
        due_date: date,
        notes: str | None,
    ) -> BillingRecord:
        resident = db.execute(select(User).where(User.id == resident_user_id)).scalar_one_or_none()
        if resident is None:
            logger.warning("Billing create failed: resident not found resident_user_id=%s", resident_user_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident user not found")

        if resident.role != UserRole.resident:
            logger.warning("Billing create rejected: target user is not resident resident_user_id=%s", resident_user_id)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Billing can only target residents")

        reference_code = generate_reference("BILL", 10)

        record = BillingRecord(
            resident_user_id=resident_user_id,
            reference_code=reference_code,
            amount_due=amount_due,
            due_date=due_date,
            status=BillingStatus.pending,
            notes=notes,
        )

        try:
            db.add(record)
            db.commit()
            logger.info(
                "Billing record created billing_id=%s resident_user_id=%s reference=%s",
                record.id,
                resident_user_id,
                reference_code,
            )
        except SQLAlchemyError:
            db.rollback()
            logger.error(
                "Billing create database error resident_user_id=%s reference=%s",
                resident_user_id,
                reference_code,
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create billing record",
            )

        return BillingService.get_billing_record_or_404(db, record.id)

    @staticmethod
    def get_billing_records(db: Session, current_user: User) -> list[BillingRecord]:
        BillingService._require_billing_visibility_role(current_user)
        query = BillingService._base_query().order_by(BillingRecord.created_at.desc())

        if current_user.role == UserRole.resident:
            query = query.where(BillingRecord.resident_user_id == current_user.id)

        return list(db.execute(query).scalars().unique().all())

    @staticmethod
    def upload_payment_proof(
        db: Session,
        billing_id: int,
        current_user: User,
        payment_method: PaymentMethod,
        amount: Decimal,
        payment_date: date,
        reference_number: str | None,
        proof_file: UploadFile,
    ) -> PaymentEvidence:
        record = BillingService.get_billing_record_or_404(db, billing_id)
        BillingService._ensure_record_access(record, current_user)

        if amount <= 0:
            logger.warning("Upload proof rejected: non-positive amount billing_id=%s user_id=%s", billing_id, current_user.id)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Amount must be greater than 0")

        file_bytes = proof_file.file.read()
        file_size = len(file_bytes)
        validate_billing_proof_file(proof_file, file_size)

        upload_dir = ensure_billing_proof_upload_directory()
        stored_name = build_proof_storage_filename(proof_file.filename)
        stored_path = upload_dir / stored_name

        evidence = PaymentEvidence(
            billing_record_id=record.id,
            submitted_by_user_id=current_user.id,
            evidence_type=EvidenceType.payment,
            payment_method=payment_method,
            reference_number=reference_number,
            amount=amount,
            payment_date=payment_date,
            file_name=proof_file.filename or stored_name,
            file_mime_type=proof_file.content_type or "application/octet-stream",
            file_size_bytes=file_size,
        )

        try:
            stored_path.write_bytes(file_bytes)
            db.add(evidence)
            record.status = BillingStatus.paid
            db.add(record)
            db.commit()
            logger.info(
                "Payment proof uploaded evidence_id=%s billing_id=%s user_id=%s",
                evidence.id,
                record.id,
                current_user.id,
            )
        except OSError:
            db.rollback()
            logger.error(
                "Payment proof file write failed billing_id=%s user_id=%s path=%s",
                billing_id,
                current_user.id,
                stored_path,
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store proof file",
            )
        except SQLAlchemyError:
            db.rollback()
            logger.error(
                "Payment proof database save failed billing_id=%s user_id=%s",
                billing_id,
                current_user.id,
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save payment proof",
            )

        return evidence

    @staticmethod
    def request_refund(
        db: Session,
        billing_id: int,
        current_user: User,
        amount: Decimal,
        reason: str,
    ) -> BillingRecord:
        record = BillingService.get_billing_record_or_404(db, billing_id)
        BillingService._ensure_record_access(record, current_user)

        if amount > record.amount_due:
            logger.warning(
                "Refund rejected: amount exceeds due billing_id=%s requested=%s due=%s user_id=%s",
                billing_id,
                amount,
                record.amount_due,
                current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund amount cannot exceed billed amount",
            )

        evidence = PaymentEvidence(
            billing_record_id=record.id,
            submitted_by_user_id=current_user.id,
            evidence_type=EvidenceType.refund_request,
            payment_method=None,
            reference_number=generate_reference("REFUND", 8),
            amount=amount,
            payment_date=date.today(),
            file_name=f"refund-{record.id}.json",
            file_mime_type="application/json",
            file_size_bytes=len(reason.encode("utf-8")),
        )

        record.amount_due = record.amount_due - amount
        record.status = BillingStatus.refunded
        if record.notes:
            record.notes = f"{record.notes}\nRefund request: {reason}"
        else:
            record.notes = f"Refund request: {reason}"

        try:
            db.add(evidence)
            db.add(record)
            db.commit()
            logger.info(
                "Refund requested billing_id=%s user_id=%s credit_amount=%s",
                billing_id,
                current_user.id,
                amount,
            )
        except SQLAlchemyError:
            db.rollback()
            logger.error(
                "Refund request database error billing_id=%s user_id=%s",
                billing_id,
                current_user.id,
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to request refund",
            )

        return BillingService.get_billing_record_or_404(db, record.id)

    @staticmethod
    def download_statement(
        db: Session,
        billing_id: int,
        current_user: User,
        fmt: StatementFormat,
    ) -> dict | Response:
        record = BillingService.get_billing_record_or_404(db, billing_id)
        BillingService._ensure_record_access(record, current_user)

        statement_payload = {
            "billing_id": record.id,
            "reference_code": record.reference_code,
            "resident_user_id": record.resident_user_id,
            "amount_due": str(record.amount_due),
            "due_date": record.due_date.isoformat(),
            "status": record.status.value,
            "notes": record.notes,
        }

        if fmt == StatementFormat.json:
            return statement_payload

        mock_pdf_text = (
            "HarborView Statement\n"
            f"Reference: {record.reference_code}\n"
            f"Resident ID: {record.resident_user_id}\n"
            f"Amount Due: {record.amount_due}\n"
            f"Due Date: {record.due_date}\n"
            f"Status: {record.status.value}\n"
        )
        return Response(content=mock_pdf_text.encode("utf-8"), media_type="application/pdf")

    @staticmethod
    def get_billing_record_or_404(db: Session, billing_id: int) -> BillingRecord:
        record = db.execute(
            BillingService._base_query().where(BillingRecord.id == billing_id)
        ).scalars().unique().one_or_none()

        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Billing record not found")

        return record

    @staticmethod
    def _require_billing_visibility_role(current_user: User) -> None:
        if current_user.role not in {UserRole.admin, UserRole.manager, UserRole.clerk, UserRole.resident}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access billing records")

    @staticmethod
    def _ensure_record_access(record: BillingRecord, current_user: User) -> None:
        BillingService._require_billing_visibility_role(current_user)
        if current_user.role == UserRole.resident and record.resident_user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access another resident billing record")
