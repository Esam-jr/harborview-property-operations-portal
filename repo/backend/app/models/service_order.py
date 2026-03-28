from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ServiceOrderStatus
from app.models.mixins import TimestampMixin


class ServiceOrder(Base, TimestampMixin):
    __tablename__ = "service_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resident_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    assigned_to_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[ServiceOrderStatus] = mapped_column(
        Enum(ServiceOrderStatus, name="service_order_status"),
        nullable=False,
        default=ServiceOrderStatus.pending,
    )

    resident: Mapped["User"] = relationship(
        foreign_keys=[resident_user_id],
        back_populates="requested_service_orders",
    )
    assignee: Mapped["User | None"] = relationship(
        foreign_keys=[assigned_to_user_id],
        back_populates="assigned_service_orders",
    )
    status_history: Mapped[list["ServiceOrderStatusHistory"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="ServiceOrderStatusHistory.changed_at",
    )


from app.models.service_order_status_history import ServiceOrderStatusHistory  # noqa: E402,F401
from app.models.user import User  # noqa: E402,F401
