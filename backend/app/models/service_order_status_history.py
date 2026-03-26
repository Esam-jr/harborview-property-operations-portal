from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ServiceOrderStatus


class ServiceOrderStatusHistory(Base):
    __tablename__ = "service_order_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("service_orders.id"), nullable=False, index=True)
    status: Mapped[ServiceOrderStatus] = mapped_column(
        Enum(ServiceOrderStatus, name="service_order_status"),
        nullable=False,
    )
    changed_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    order: Mapped["ServiceOrder"] = relationship(back_populates="status_history")
    changed_by: Mapped["User"] = relationship(back_populates="order_status_changes")


from app.models.service_order import ServiceOrder  # noqa: E402,F401
from app.models.user import User  # noqa: E402,F401
