from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ServiceOrderStatus, UserRole


class OrderCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=3)
    due_date: datetime | None = None


class OrderStatusUpdateRequest(BaseModel):
    status: ServiceOrderStatus
    assigned_to_user_id: int | None = None
    note: str | None = Field(default=None, max_length=1000)


class OrderStatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    status: ServiceOrderStatus
    changed_by_user_id: int
    changed_at: datetime
    note: str | None = None


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resident_user_id: int
    assigned_to_user_id: int | None
    title: str
    description: str
    due_date: datetime | None = None
    status: ServiceOrderStatus
    created_at: datetime
    updated_at: datetime
    status_history: list[OrderStatusHistoryRead]


class ServiceOrderAssigneeValidation(BaseModel):
    assignee_id: int
    assignee_role: UserRole


# Backward-compatible aliases for existing imports.
ServiceOrderCreate = OrderCreateRequest
ServiceOrderStatusUpdate = OrderStatusUpdateRequest
ServiceOrderStatusHistoryRead = OrderStatusHistoryRead
ServiceOrderRead = OrderRead
