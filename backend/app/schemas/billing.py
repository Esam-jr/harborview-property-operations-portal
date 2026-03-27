from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BillingStatus, PaymentMethod, StatementFormat


class BillingCreate(BaseModel):
    resident_user_id: int
    amount_due: Decimal = Field(gt=0)
    due_date: date
    notes: str | None = None


class BillingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resident_user_id: int
    reference_code: str
    amount_due: Decimal
    due_date: date
    status: BillingStatus
    notes: str | None


class UploadProofResponse(BaseModel):
    evidence_id: int
    billing_id: int
    file_name: str
    file_mime_type: str
    file_size_bytes: int
    payment_method: PaymentMethod


class UploadProofRequest(BaseModel):
    payment_method: PaymentMethod
    amount: Decimal = Field(gt=0)
    payment_date: date
    reference_number: str | None = None


class RefundRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    reason: str = Field(min_length=3, max_length=500)


class RefundResponse(BaseModel):
    billing_id: int
    credit_amount: Decimal
    status: BillingStatus
    message: str


class BillingStatementResponse(BaseModel):
    billing_id: int
    format: StatementFormat
    data: dict
