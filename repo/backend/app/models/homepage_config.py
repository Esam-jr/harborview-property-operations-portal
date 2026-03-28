from typing import Any

from sqlalchemy import JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class HomePageConfig(Base, TimestampMixin):
    __tablename__ = "homepage_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)

    json_type = JSON().with_variant(JSONB, "postgresql")

    live_carousel_panels: Mapped[list[dict[str, Any]]] = mapped_column(json_type, default=list, nullable=False)
    live_recommended_tiles: Mapped[list[dict[str, Any]]] = mapped_column(json_type, default=list, nullable=False)
    live_announcement_banners: Mapped[list[dict[str, Any]]] = mapped_column(json_type, default=list, nullable=False)

    staged_carousel_panels: Mapped[list[dict[str, Any]]] = mapped_column(json_type, default=list, nullable=False)
    staged_recommended_tiles: Mapped[list[dict[str, Any]]] = mapped_column(json_type, default=list, nullable=False)
    staged_announcement_banners: Mapped[list[dict[str, Any]]] = mapped_column(json_type, default=list, nullable=False)

    preview_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rollout_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rollout_percentage: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    full_enablement: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
