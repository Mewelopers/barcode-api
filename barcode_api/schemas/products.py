import uuid

import barcode  # type: ignore
from barcode_api.utils.optional import make_optional
from pydantic import BaseModel, Field, validator

from .db_base import TrackedDbSchema


class ProductSearch(BaseModel):
    """
    Base schema used when searching for a product
    """

    barcode: str = Field(..., min_length=8, max_length=14, regex=r"^[0-9]+$")

    @validator("barcode")
    def validate_barcode(cls, v: str) -> str:
        barcode_type = len(v)

        match barcode_type:
            case 8:
                checker = barcode.EAN8
            case 13:
                checker = barcode.EAN13
            case 14:
                checker = barcode.EAN14
            case _:
                raise ValueError("Invalid barcode length")

        return checker(v).get_fullcode()  # type: ignore


class ProductMedia(BaseModel):
    """
    Schema used when interacting with image fields of a product
    """

    thumbnail: bytes | None = Field(None)
    barcode_image: bytes | None = Field(None)


class ProductMediaIds(BaseModel):
    """
    Id of the media files associated with a product
    """

    class Config:
        orm_mode = True

    thumbnail_uuid: uuid.UUID | None = Field(None)
    barcode_image_uuid: uuid.UUID | None = Field(None)


class ProductCommon(ProductSearch):
    """
    Common information about a product
    """

    class Config:
        orm_mode = True

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1, max_length=10000)
    manufacturer: str | None = Field(None, min_length=1, max_length=255)


class ProductCreate(ProductCommon, ProductMedia):
    """
    Schema used when creating a product
    """

    ...


class ProductResponse(ProductCommon, ProductMediaIds):
    class Config:
        orm_mode = True

    id: int
    thumbnail_url: str | None
    barcode_image_url: str | None


@make_optional(exclude=["id"])
class ProductUpdate(ProductCreate):
    id: int


class ProductInDb(ProductCreate, TrackedDbSchema, ProductMediaIds):
    class Config:
        orm_mode = True

    id: int
