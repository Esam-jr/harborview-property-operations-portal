from sqlalchemy import Enum, ForeignKey, Integer, String, Text
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
    status: Mapped[ServiceOrderStatus] = mapped_column(
        Enum(ServiceOrderStatus, name="service_order_status"),
        nullable=False,
        default=ServiceOrderStatus.submitted,
    )

    resident: Mapped["User"] = relationship(
        foreign_keys=[resident_user_id],
        back_populates="requested_service_orders",
    )
    assignee: Mapped["User | None"] = relationship(
        foreign_keys=[assigned_to_user_id],
        back_populates="assigned_service_orders",
    )


from app.models.user import User  # noqa: E402,F401
