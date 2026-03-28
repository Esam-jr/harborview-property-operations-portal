from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import BillingStatus
from app.models.mixins import TimestampMixin


class BillingRecord(Base, TimestampMixin):
    __tablename__ = "billing_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resident_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    reference_code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    amount_due: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[BillingStatus] = mapped_column(
        Enum(BillingStatus, name="billing_status"),
        nullable=False,
        default=BillingStatus.pending,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    resident: Mapped["User"] = relationship(back_populates="billing_records")
    payment_evidences: Mapped[list["PaymentEvidence"]] = relationship(
        back_populates="billing_record",
        cascade="all, delete-orphan",
    )


from app.models.payment_evidence import PaymentEvidence  # noqa: E402,F401
from app.models.user import User  # noqa: E402,F401
