from pydantic import BaseModel, Field

from app.models.enums import UserRole


class ResidentProfileRead(BaseModel):
    id: int
    username: str
    role: UserRole
    shipping_address: str | None = None
    mailing_address: str | None = None


class ResidentAddressUpdate(BaseModel):
    shipping_address: str | None = Field(default=None, max_length=500)
    mailing_address: str | None = Field(default=None, max_length=500)
