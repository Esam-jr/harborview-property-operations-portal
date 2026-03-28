from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import UserRole


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    role: UserRole


class UserRegister(BaseModel):
    model_config = ConfigDict(extra="ignore")

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    shipping_address: str | None = None
    mailing_address: str | None = None


class StaffProvisionRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    role: UserRole
    shipping_address: str | None = None
    mailing_address: str | None = None

    @field_validator("role")
    @classmethod
    def validate_staff_role(cls, value: UserRole) -> UserRole:
        if value == UserRole.resident:
            raise ValueError("Staff account role cannot be resident")
        return value


class UserLogin(BaseModel):
    username: str
    password: str = Field(min_length=8)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shipping_address: str | None = None
    mailing_address: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class AuthenticatedUser(BaseModel):
    username: str
    role: UserRole
    shipping_address: str | None = None
    mailing_address: str | None = None


class ProtectedMessage(BaseModel):
    message: str
    user: AuthenticatedUser
    timestamp: datetime
