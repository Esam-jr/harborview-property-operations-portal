import logging
from datetime import timedelta

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "HarborView Property Operations Portal"
    app_environment: str = "development"

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "harborview"
    db_user: str = "harborview"
    db_password: str = "harborview"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    listing_upload_dir: str = "storage/listings"
    listing_allowed_image_types: str = "image/jpeg,image/png"
    listing_allowed_video_types: str = "video/mp4"
    listing_max_image_size_bytes: int = 10 * 1024 * 1024
    listing_max_video_size_bytes: int = 200 * 1024 * 1024

    billing_proof_upload_dir: str = "storage/billing-proofs"
    billing_allowed_image_types: str = "image/jpeg,image/png"
    billing_max_image_size_bytes: int = 10 * 1024 * 1024

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @computed_field
    @property
    def access_token_expire_delta(self) -> timedelta:
        return timedelta(minutes=self.jwt_access_token_expire_minutes)

    @computed_field
    @property
    def allowed_image_types(self) -> set[str]:
        return {value.strip() for value in self.listing_allowed_image_types.split(",") if value.strip()}

    @computed_field
    @property
    def allowed_video_types(self) -> set[str]:
        return {value.strip() for value in self.listing_allowed_video_types.split(",") if value.strip()}

    @computed_field
    @property
    def billing_allowed_proof_types(self) -> set[str]:
        return {value.strip() for value in self.billing_allowed_image_types.split(",") if value.strip()}

    @computed_field
    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


def _resolve_log_level(app_environment: str) -> int:
    if app_environment.lower() in {"dev", "development", "local"}:
        return logging.INFO
    return logging.WARNING


def configure_logging(app_environment: str) -> None:
    logging.basicConfig(
        level=_resolve_log_level(app_environment),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


settings = Settings()
configure_logging(settings.app_environment)
