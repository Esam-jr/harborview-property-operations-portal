from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.service_order import ServiceOrderCreate, ServiceOrderRead, ServiceOrderStatusUpdate
from app.services.service_order_service import ServiceOrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=ServiceOrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: ServiceOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceOrderRead:
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
    )
    return ServiceOrderRead.model_validate(order)


@router.get("", response_model=list[ServiceOrderRead])
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ServiceOrderRead]:
    orders = ServiceOrderService.get_orders(db=db, current_user=current_user)
    return [ServiceOrderRead.model_validate(order) for order in orders]


@router.patch("/{order_id}/status", response_model=ServiceOrderRead)
def update_order_status(
    order_id: int,
    payload: ServiceOrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceOrderRead:
    if current_user.role not in {UserRole.admin, UserRole.manager, UserRole.dispatcher}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, manager, or dispatcher can update order status",
        )

    order = ServiceOrderService.update_status(
        db=db,
        order_id=order_id,
        new_status=payload.status,
        changed_by_user=current_user,
        assigned_to_user_id=payload.assigned_to_user_id,
    )
    return ServiceOrderRead.model_validate(order)
