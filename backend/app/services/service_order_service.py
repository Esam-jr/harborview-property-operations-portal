from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.models.enums import ServiceOrderStatus, UserRole
from app.models.service_order import ServiceOrder
from app.models.service_order_status_history import ServiceOrderStatusHistory
from app.models.user import User


class ServiceOrderService:
    @staticmethod
    def _base_query() -> Select:
        return select(ServiceOrder).options(joinedload(ServiceOrder.status_history))

    @staticmethod
    def create_order(
        db: Session,
        resident_user_id: int,
        title: str,
        description: str,
        due_date: datetime | None = None,
    ) -> ServiceOrder:
        order = ServiceOrder(
            resident_user_id=resident_user_id,
            title=title.strip(),
            description=description.strip(),
            due_date=due_date,
            status=ServiceOrderStatus.pending,
        )

        try:
            db.add(order)
            db.flush()

            history = ServiceOrderStatusHistory(
                order_id=order.id,
                status=ServiceOrderStatus.pending,
                changed_by_user_id=resident_user_id,
                note="Order submitted",
            )
            db.add(history)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create service order",
            )

        return ServiceOrderService.get_by_id_or_404(db, order.id)

    @staticmethod
    def get_orders(db: Session, current_user: User, assigned_only: bool = False) -> list[ServiceOrder]:
        query = ServiceOrderService._base_query().order_by(ServiceOrder.created_at.desc())

        if current_user.role == UserRole.resident:
            query = query.where(ServiceOrder.resident_user_id == current_user.id)
        elif assigned_only:
            query = query.where(ServiceOrder.assigned_to_user_id == current_user.id)

        return list(db.execute(query).scalars().unique().all())

    @staticmethod
    def update_status(
        db: Session,
        order_id: int,
        new_status: ServiceOrderStatus,
        changed_by_user_id: int | None = None,
        changed_by_user: User | None = None,
        assigned_to_user_id: int | None = None,
        note: str | None = None,
    ) -> ServiceOrder:
        order = ServiceOrderService.get_by_id_or_404(db, order_id)
        actor_user: User | None = changed_by_user
        if actor_user is None and changed_by_user_id is not None:
            actor_user = db.execute(select(User).where(User.id == changed_by_user_id)).scalar_one_or_none()

        changed_by_user = actor_user
        if changed_by_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if changed_by_user.role not in {UserRole.dispatcher, UserRole.manager, UserRole.admin}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only dispatcher, manager, or admin can update order status",
            )

        if assigned_to_user_id is not None:
            assignee = db.execute(select(User).where(User.id == assigned_to_user_id)).scalar_one_or_none()
            if assignee is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee user not found")
            if assignee.role != UserRole.dispatcher:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assignee must have dispatcher role",
                )
            order.assigned_to_user_id = assigned_to_user_id

        if changed_by_user.role == UserRole.dispatcher and order.assigned_to_user_id not in (
            None,
            changed_by_user.id,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Dispatcher can only update unassigned or self-assigned orders",
            )

        if new_status == ServiceOrderStatus.in_progress and order.assigned_to_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order must be assigned to a dispatcher before moving to in_progress",
            )

        order.status = new_status

        history = ServiceOrderStatusHistory(
            order_id=order.id,
            status=new_status,
            changed_by_user_id=changed_by_user.id,
            note=note,
        )

        try:
            db.add(order)
            db.add(history)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update service order status",
            )

        return ServiceOrderService.get_by_id_or_404(db, order.id)

    @staticmethod
    def get_by_id_or_404(db: Session, order_id: int) -> ServiceOrder:
        order = db.execute(
            ServiceOrderService._base_query().where(ServiceOrder.id == order_id)
        ).scalars().unique().one_or_none()

        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found")

        return order
