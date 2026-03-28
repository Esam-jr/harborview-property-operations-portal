from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import EvidenceType, PaymentMethod
from app.models.mixins import TimestampMixin


class PaymentEvidence(Base, TimestampMixin):
    __tablename__ = "payment_evidences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    billing_record_id: Mapped[int] = mapped_column(ForeignKey("billing_records.id"), nullable=False, index=True)
    submitted_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    evidence_type: Mapped[EvidenceType] = mapped_column(
        Enum(EvidenceType, name="evidence_type"),
        nullable=False,
        default=EvidenceType.payment,
    )
    payment_method: Mapped[PaymentMethod | None] = mapped_column(
        Enum(PaymentMethod, name="payment_method"),
        nullable=True,
    )
    reference_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    billing_record: Mapped["BillingRecord"] = relationship(back_populates="payment_evidences")
    submitted_by: Mapped["User"] = relationship(back_populates="submitted_payment_evidences")


from app.models.billing_record import BillingRecord  # noqa: E402,F401
from app.models.user import User  # noqa: E402,F401
