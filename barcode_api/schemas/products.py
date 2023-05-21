import barcode  # type: ignore
from barcode_api.utils.optional import make_optional
from pydantic import BaseModel, Field, validator

from .db_base import TrackedDbSchema


class ProductSearch(BaseModel):
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


class ProdyctMedia(BaseModel):
    thumbnail: bytes | None = Field(None)
    barcode_image: bytes | None = Field(None)


class ProductCommon(ProductSearch):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1, max_length=10000)
    manufacturer: str | None = Field(None, min_length=1, max_length=255)


class ProductCreate(ProductCommon, ProdyctMedia):
    ...


class ProductResponse(ProductCommon):
    class Config:
        orm_mode = True

    id: int
    thumbnail_url: str | None = Field(None)
    barcode_image_url: str | None = Field(None)


@make_optional(exclude=["id"])
class ProductUpdate(ProductCreate):
    id: int


class ProductInDb(ProductCreate, TrackedDbSchema):
    id: int
    thumbnail_uuid: str | None = Field(None)
    barcode_image_uuid: str | None = Field(None)

    class Config:
        orm_mode = True
