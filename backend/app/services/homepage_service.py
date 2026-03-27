from hashlib import sha256

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

        return HomePageConfigRead(
            live=HomePageSections(
                carousel_panels=config.live_carousel_panels,
                recommended_tiles=config.live_recommended_tiles,
                announcement_banners=config.live_announcement_banners,
            ),
            staged=HomePageSections(
                carousel_panels=config.staged_carousel_panels,
                recommended_tiles=config.staged_recommended_tiles,
                announcement_banners=config.staged_announcement_banners,
            ),
            preview_enabled=config.preview_enabled,
            rollout_enabled=config.rollout_enabled,
            rollout_percentage=config.rollout_percentage,
            full_enablement=config.full_enablement,
        )

    @staticmethod
    def update_admin_config(db: Session, current_user: User, payload: HomePageConfigUpdate) -> HomePageConfigRead:
        HomePageService._require_admin(current_user)
        config = HomePageService._bootstrap_if_missing(db)

        config.staged_carousel_panels = payload.staged.carousel_panels
        config.staged_recommended_tiles = payload.staged.recommended_tiles
        config.staged_announcement_banners = payload.staged.announcement_banners

        config.preview_enabled = payload.preview_enabled
        config.rollout_enabled = payload.rollout_enabled
        config.rollout_percentage = payload.rollout_percentage
        config.full_enablement = payload.full_enablement

        if payload.full_enablement:
            config.live_carousel_panels = payload.staged.carousel_panels
            config.live_recommended_tiles = payload.staged.recommended_tiles
            config.live_announcement_banners = payload.staged.announcement_banners

        try:
            db.add(config)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update homepage config",
            )

        return HomePageService.get_admin_config(db, current_user)

    @staticmethod
    def get_homepage_for_user(db: Session, current_user: User) -> HomePageContentRead:
        config = HomePageService._bootstrap_if_missing(db)
        use_staged = HomePageService._should_use_staged(config, current_user)

        if use_staged:
            sections = HomePageSections(
                carousel_panels=config.staged_carousel_panels,
                recommended_tiles=config.staged_recommended_tiles,
                announcement_banners=config.staged_announcement_banners,
            )
            source = "staged"
        else:
            sections = HomePageSections(
                carousel_panels=config.live_carousel_panels,
                recommended_tiles=config.live_recommended_tiles,
                announcement_banners=config.live_announcement_banners,
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
