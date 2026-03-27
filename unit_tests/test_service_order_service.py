import pytest
from fastapi import HTTPException

from app.models.enums import ServiceOrderStatus, UserRole
from app.services.service_order_service import ServiceOrderService


def test_create_order_initializes_pending_history(db_session, create_user):
    resident = create_user("resident_unit", "resident-pass-123", UserRole.resident)

    order = ServiceOrderService.create_order(
        db=db_session,
        resident_user_id=resident.id,
        title="Broken hallway light",
        description="The hallway light on level 2 is out.",
    )

    assert order.id is not None
    assert order.status == ServiceOrderStatus.pending
    assert order.resident_user_id == resident.id
    assert len(order.status_history) == 1
    assert order.status_history[0].status == ServiceOrderStatus.pending


def test_update_status_requires_dispatcher_assignment_for_in_progress(db_session, create_user):
    resident = create_user("resident_status", "resident-pass-123", UserRole.resident)
    manager = create_user("manager_status", "manager-pass-123", UserRole.manager)

    order = ServiceOrderService.create_order(
        db=db_session,
        resident_user_id=resident.id,
        title="Leaking sink",
        description="Kitchen sink leaks under cabinet.",
    )

    with pytest.raises(HTTPException) as exc_info:
        ServiceOrderService.update_status(
            db=db_session,
            order_id=order.id,
            new_status=ServiceOrderStatus.in_progress,
            changed_by_user=manager,
            assigned_to_user_id=None,
        )

    assert exc_info.value.status_code == 400
    assert "assigned to a dispatcher" in str(exc_info.value.detail)


def test_update_status_with_valid_dispatcher_assignment_succeeds(db_session, create_user):
    resident = create_user("resident_ok", "resident-pass-123", UserRole.resident)
    manager = create_user("manager_ok", "manager-pass-123", UserRole.manager)
    dispatcher = create_user("dispatcher_ok", "dispatcher-pass-123", UserRole.dispatcher)

    order = ServiceOrderService.create_order(
        db=db_session,
        resident_user_id=resident.id,
        title="Elevator issue",
        description="Elevator door is not closing consistently.",
    )

    updated = ServiceOrderService.update_status(
        db=db_session,
        order_id=order.id,
        new_status=ServiceOrderStatus.in_progress,
        changed_by_user=manager,
        assigned_to_user_id=dispatcher.id,
    )

    assert updated.status == ServiceOrderStatus.in_progress
    assert updated.assigned_to_user_id == dispatcher.id
    assert len(updated.status_history) == 2
    assert updated.status_history[-1].status == ServiceOrderStatus.in_progress
