from typing import Any

from pydantic import BaseModel, Field, field_validator


class HomePageSections(BaseModel):
    carousel_panels: list[dict[str, Any]] = Field(default_factory=list)
    recommended_tiles: list[dict[str, Any]] = Field(default_factory=list)
    announcement_banners: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("carousel_panels", "recommended_tiles", "announcement_banners")
    @classmethod
    def validate_sections(cls, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if len(value) > 100:
            raise ValueError("Each homepage section supports at most 100 items")
        for item in value:
            if not isinstance(item, dict):
                raise ValueError("Each section entry must be a JSON object")
            if len(item) > 50:
                raise ValueError("Each section entry supports at most 50 fields")
        return value


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
