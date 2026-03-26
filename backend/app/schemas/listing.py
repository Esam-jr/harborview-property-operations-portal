from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import ListingMediaType, ListingStatus


class ListingMediaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    media_type: ListingMediaType
    file_name: str
    file_path: str
    mime_type: str
    file_size_bytes: int


class ListingBase(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=3)
    price_amount: Decimal | None = Field(default=None, ge=0)


class ListingCreate(ListingBase):
    status: ListingStatus = ListingStatus.draft


class ListingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, min_length=3)
    price_amount: Decimal | None = Field(default=None, ge=0)
    status: ListingStatus | None = None


class ListingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_user_id: int
    title: str
    description: str
    price_amount: Decimal | None
    status: ListingStatus
    media_items: list[ListingMediaRead]


class ListingBulkUpdateRequest(BaseModel):
    ids: list[int] = Field(min_length=1)
    status: ListingStatus

    @field_validator("ids")
    @classmethod
    def unique_ids(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("Listing IDs must be unique")
        return value


class ListingBulkUpdateResponse(BaseModel):
    updated_count: int
    status: ListingStatus


class ListingQueryParams(BaseModel):
    status: ListingStatus | None = None
    owner_user_id: int | None = None
