from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import UserRole


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    role: UserRole


class UserRegister(UserBase):
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str = Field(min_length=8)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class AuthenticatedUser(BaseModel):
    username: str
    role: UserRole


class ProtectedMessage(BaseModel):
    message: str
    user: AuthenticatedUser
    timestamp: datetime
