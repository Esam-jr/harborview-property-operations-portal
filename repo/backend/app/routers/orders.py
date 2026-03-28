from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.service_order import OrderCreateRequest, OrderRead, OrderStatusUpdateRequest
from app.services.service_order_service import ServiceOrderService

router = APIRouter(prefix="/orders", tags=["orders"])


def _require_dispatcher_or_manager(user: User) -> None:
    if user.role not in {UserRole.dispatcher, UserRole.manager, UserRole.admin}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only dispatcher, manager, or admin can update order status",
        )


def _ensure_can_view_order(order, user: User) -> None:
    if user.role == UserRole.resident and order.resident_user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this order",
        )


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderRead:
    if current_user.role != UserRole.resident:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only residents can create service orders",
        )

    order = ServiceOrderService.create_order(
        db=db,
        resident_user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date,
    )
    return OrderRead.model_validate(order)


@router.get("", response_model=list[OrderRead])
def get_orders(
    assigned_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[OrderRead]:
    orders = ServiceOrderService.get_orders(
        db=db,
        current_user=current_user,
        assigned_only=assigned_only,
    )
    return [OrderRead.model_validate(order) for order in orders]


@router.get("/{order_id}", response_model=OrderRead)
def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderRead:
    order = ServiceOrderService.get_by_id_or_404(db=db, order_id=order_id)
    _ensure_can_view_order(order, current_user)
    return OrderRead.model_validate(order)


@router.put("/{order_id}/status", response_model=OrderRead)
@router.patch("/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderRead:
    _require_dispatcher_or_manager(current_user)

    order = ServiceOrderService.update_status(
        db=db,
        order_id=order_id,
        new_status=payload.status,
        changed_by_user_id=current_user.id,
        assigned_to_user_id=payload.assigned_to_user_id,
        note=payload.note,
    )
    return OrderRead.model_validate(order)
