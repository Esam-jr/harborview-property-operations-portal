from sqlalchemy import Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import UserRole
from app.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    shipping_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    mailing_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    property_listings: Mapped[list["PropertyListing"]] = relationship(back_populates="owner")
    requested_service_orders: Mapped[list["ServiceOrder"]] = relationship(
        foreign_keys="ServiceOrder.resident_user_id",
        back_populates="resident",
    )
    assigned_service_orders: Mapped[list["ServiceOrder"]] = relationship(
        foreign_keys="ServiceOrder.assigned_to_user_id",
        back_populates="assignee",
    )
    order_status_changes: Mapped[list["ServiceOrderStatusHistory"]] = relationship(
        back_populates="changed_by"
    )
    billing_records: Mapped[list["BillingRecord"]] = relationship(back_populates="resident")
    submitted_payment_evidences: Mapped[list["PaymentEvidence"]] = relationship(
        back_populates="submitted_by"
    )


from app.models.billing_record import BillingRecord  # noqa: E402,F401
from app.models.payment_evidence import PaymentEvidence  # noqa: E402,F401
from app.models.property_listing import PropertyListing  # noqa: E402,F401
from app.models.service_order import ServiceOrder  # noqa: E402,F401
from app.models.service_order_status_history import ServiceOrderStatusHistory  # noqa: E402,F401
