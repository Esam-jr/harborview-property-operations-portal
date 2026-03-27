from hashlib import sha256
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.homepage_config import HomePageConfig
from app.models.user import User
from app.schemas.homepage import HomePageConfigRead, HomePageConfigUpdate, HomePageContentRead, HomePageSections


class HomePageService:
    @staticmethod
    def _bootstrap_if_missing(db: Session) -> HomePageConfig:
        config = db.execute(select(HomePageConfig).where(HomePageConfig.id == 1)).scalar_one_or_none()
        if config:
            return config

        config = HomePageConfig(id=1)
        db.add(config)
        db.commit()
        db.refresh(config)
        return config

    @staticmethod
    def get_admin_config(db: Session, current_user: User) -> HomePageConfigRead:
        HomePageService._require_admin(current_user)
        config = HomePageService._bootstrap_if_missing(db)
        return HomePageService._to_config_read(config)

    @staticmethod
    def update_admin_config(db: Session, current_user: User, payload: HomePageConfigUpdate) -> HomePageConfigRead:
        HomePageService._require_admin(current_user)
        config = HomePageService._bootstrap_if_missing(db)

        staged_sections = HomePageService._sanitize_sections(payload.staged)

        config.staged_carousel_panels = staged_sections.carousel_panels
        config.staged_recommended_tiles = staged_sections.recommended_tiles
        config.staged_announcement_banners = staged_sections.announcement_banners

        config.preview_enabled = payload.preview_enabled
        config.rollout_enabled = payload.rollout_enabled
        config.rollout_percentage = payload.rollout_percentage
        config.full_enablement = payload.full_enablement

        if payload.full_enablement:
            config.live_carousel_panels = staged_sections.carousel_panels
            config.live_recommended_tiles = staged_sections.recommended_tiles
            config.live_announcement_banners = staged_sections.announcement_banners

        try:
            db.add(config)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update homepage config",
            )

        refreshed = HomePageService._bootstrap_if_missing(db)
        return HomePageService._to_config_read(refreshed)

    @staticmethod
    def get_homepage_for_user(db: Session, current_user: User) -> HomePageContentRead:
        config = HomePageService._bootstrap_if_missing(db)
        use_staged = HomePageService._should_use_staged(config, current_user)

        if use_staged:
            sections = HomePageSections(
                carousel_panels=HomePageService._normalize_list(config.staged_carousel_panels),
                recommended_tiles=HomePageService._normalize_list(config.staged_recommended_tiles),
                announcement_banners=HomePageService._normalize_list(config.staged_announcement_banners),
            )
            source = "staged"
        else:
            sections = HomePageSections(
                carousel_panels=HomePageService._normalize_list(config.live_carousel_panels),
                recommended_tiles=HomePageService._normalize_list(config.live_recommended_tiles),
                announcement_banners=HomePageService._normalize_list(config.live_announcement_banners),
            )
            source = "live"

        return HomePageContentRead(
            sections=sections,
            source=source,
            preview_enabled=config.preview_enabled,
            rollout_enabled=config.rollout_enabled,
            rollout_percentage=config.rollout_percentage,
            full_enablement=config.full_enablement,
        )

    @staticmethod
    def _to_config_read(config: HomePageConfig) -> HomePageConfigRead:
        return HomePageConfigRead(
            live=HomePageSections(
                carousel_panels=HomePageService._normalize_list(config.live_carousel_panels),
                recommended_tiles=HomePageService._normalize_list(config.live_recommended_tiles),
                announcement_banners=HomePageService._normalize_list(config.live_announcement_banners),
            ),
            staged=HomePageSections(
                carousel_panels=HomePageService._normalize_list(config.staged_carousel_panels),
                recommended_tiles=HomePageService._normalize_list(config.staged_recommended_tiles),
                announcement_banners=HomePageService._normalize_list(config.staged_announcement_banners),
            ),
            preview_enabled=config.preview_enabled,
            rollout_enabled=config.rollout_enabled,
            rollout_percentage=config.rollout_percentage,
            full_enablement=config.full_enablement,
        )

    @staticmethod
    def _sanitize_sections(sections: HomePageSections) -> HomePageSections:
        return HomePageSections(
            carousel_panels=HomePageService._sanitize_list(sections.carousel_panels),
            recommended_tiles=HomePageService._sanitize_list(sections.recommended_tiles),
            announcement_banners=HomePageService._sanitize_list(sections.announcement_banners),
        )

    @staticmethod
    def _sanitize_list(value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized = HomePageService._normalize_list(value)
        return [
            HomePageService._sanitize_object(item, depth=0)
            for item in normalized
        ]

    @staticmethod
    def _normalize_list(value: Any) -> list[dict[str, Any]]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Homepage section payload must be a JSON array",
            )
        return value

    @staticmethod
    def _sanitize_object(item: Any, depth: int) -> dict[str, Any]:
        if depth > 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Homepage JSON nesting is too deep",
            )
        if not isinstance(item, dict):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Each homepage section entry must be a JSON object",
            )

        sanitized: dict[str, Any] = {}
        for key, value in item.items():
            if not isinstance(key, str):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Homepage JSON keys must be strings",
                )
            if len(key) > 100:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Homepage JSON key length exceeds 100 characters",
                )
            sanitized[key] = HomePageService._sanitize_value(value, depth + 1)
        return sanitized

    @staticmethod
    def _sanitize_value(value: Any, depth: int) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value

        if isinstance(value, list):
            return [HomePageService._sanitize_value(item, depth + 1) for item in value]

        if isinstance(value, dict):
            return HomePageService._sanitize_object(value, depth + 1)

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Homepage payload contains unsupported JSON value types",
        )

    @staticmethod
    def _should_use_staged(config: HomePageConfig, user: User) -> bool:
        if config.full_enablement:
            return False

        if user.role == UserRole.admin and config.preview_enabled:
            return True

        staff_roles = {UserRole.admin, UserRole.manager, UserRole.clerk, UserRole.dispatcher}
        if config.rollout_enabled and user.role in staff_roles:
            digest = sha256(f"{user.id}:{user.username}".encode("utf-8")).hexdigest()
            bucket = int(digest[:8], 16) % 100
            return bucket < config.rollout_percentage

        return False

    @staticmethod
    def _require_admin(user: User) -> None:
        if user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin role can manage homepage configuration",
            )
