from typing import Any

from pydantic import BaseModel, Field


class HomePageSections(BaseModel):
    carousel_panels: list[dict[str, Any]] = Field(default_factory=list)
    recommended_tiles: list[dict[str, Any]] = Field(default_factory=list)
    announcement_banners: list[dict[str, Any]] = Field(default_factory=list)


class HomePageConfigRead(BaseModel):
    live: HomePageSections
    staged: HomePageSections
    preview_enabled: bool
    rollout_enabled: bool
    rollout_percentage: int
    full_enablement: bool


class HomePageConfigUpdate(BaseModel):
    staged: HomePageSections
    preview_enabled: bool = False
    rollout_enabled: bool = False
    rollout_percentage: int = Field(default=10, ge=0, le=100)
    full_enablement: bool = False


class HomePageContentRead(BaseModel):
    sections: HomePageSections
    source: str
    preview_enabled: bool
    rollout_enabled: bool
    rollout_percentage: int
    full_enablement: bool
