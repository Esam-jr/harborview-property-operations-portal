import pytest
from fastapi import HTTPException

from app.models.enums import UserRole
from app.schemas.homepage import HomePageConfigUpdate, HomePageSections
from app.services.homepage_service import HomePageService


def _sample_config_update() -> HomePageConfigUpdate:
    return HomePageConfigUpdate(
        staged=HomePageSections(
            carousel_panels=[{"title": "Seasonal Notice", "body": "Pool hours updated"}],
            recommended_tiles=[{"title": "Pay HOA Dues", "action": "/billing"}],
            announcement_banners=[{"title": "Maintenance Window", "message": "Water shutoff at 9AM"}],
        ),
        preview_enabled=True,
        rollout_enabled=True,
        rollout_percentage=35,
        full_enablement=False,
    )


def test_admin_can_update_homepage_configuration(db_session, create_user):
    admin_user = create_user("homepage_admin", "admin-pass-123", UserRole.admin)
    payload = _sample_config_update()

    updated = HomePageService.update_admin_config(
        db=db_session,
        current_user=admin_user,
        payload=payload,
    )

    assert updated.preview_enabled is True
    assert updated.rollout_enabled is True
    assert updated.rollout_percentage == 35
    assert updated.staged.carousel_panels[0]["title"] == "Seasonal Notice"
    assert updated.staged.recommended_tiles[0]["title"] == "Pay HOA Dues"
    assert updated.staged.announcement_banners[0]["title"] == "Maintenance Window"


def test_manager_can_update_homepage_configuration(db_session, create_user):
    manager_user = create_user("homepage_manager", "manager-pass-123", UserRole.manager)
    payload = _sample_config_update()

    updated = HomePageService.update_admin_config(
        db=db_session,
        current_user=manager_user,
        payload=payload,
    )

    assert updated.preview_enabled is True
    assert updated.rollout_enabled is True
    assert updated.rollout_percentage == 35
    assert updated.staged.carousel_panels[0]["title"] == "Seasonal Notice"


def test_resident_cannot_overwrite_homepage_configuration(db_session, create_user):
    resident_user = create_user("homepage_resident", "resident-pass-123", UserRole.resident)
    payload = _sample_config_update()

    with pytest.raises(HTTPException) as exc_info:
        HomePageService.update_admin_config(
            db=db_session,
            current_user=resident_user,
            payload=payload,
        )

    assert exc_info.value.status_code == 403
    assert "Only admin role can manage homepage configuration" in str(exc_info.value.detail)
