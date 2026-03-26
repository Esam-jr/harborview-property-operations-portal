from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ServiceOrderStatus, UserRole


class ServiceOrderCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=3)


class ServiceOrderStatusUpdate(BaseModel):
    status: ServiceOrderStatus
    assigned_to_user_id: int | None = None


class ServiceOrderStatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    status: ServiceOrderStatus
    changed_by_user_id: int
    changed_at: datetime


class ServiceOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resident_user_id: int
    assigned_to_user_id: int | None
    title: str
    description: str
    status: ServiceOrderStatus
    created_at: datetime
    updated_at: datetime
    status_history: list[ServiceOrderStatusHistoryRead]


class ServiceOrderAssigneeValidation(BaseModel):
    assignee_id: int
    assignee_role: UserRole
