import barcode  # type: ignore
from fastapi_utils.api_model import APIModel
from pydantic import BaseModel, Field, validator, UUID4

from .db_base import CreatedAtUpdatedAt, SequentialId


class ProductBarcode(BaseModel):
    """
    Schema for validating the product barcode
    """

    barcode: str = Field(..., min_length=8, max_length=14, regex=r"^[0-9]+$")

    @validator("barcode")
    def validate_barcode(cls, v: str) -> str:
        barcode_type = len(v)

        match barcode_type:
            case 8:
                checker = barcode.EAN8
            case 12:
                checker = barcode.UPCA
            case 13:
                checker = barcode.EAN13
            case 14:
                checker = barcode.EAN14
            case _:
                raise ValueError("Invalid barcode length")

        if v != checker(v).get_fullcode():
            raise ValueError("Invalid barcode")

        return checker(v).get_fullcode()  # type: ignore


class ProductSearch(BaseModel):
    limit: int = Field(10, ge=1, le=100)
    query: str | None = None


class ProductInformation(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1, max_length=10000)
    manufacturer: str | None = Field(None, min_length=1, max_length=255)


class ProductMedia(BaseModel):
    thumbnail_uuid: UUID4 | None = Field(None)
    barcode_image_uuid: UUID4 | None = Field(None)


class ProductCreate(ProductBarcode, ProductInformation):
    """
    Schema used when creating a product
    """

    class Config:
        orm_mode = True


class ProductInDb(ProductCreate, SequentialId, CreatedAtUpdatedAt, ProductMedia):
    """
    Represents a product in the database
    """

    class Config:
        orm_mode = True


class ProductResponse(ProductInformation, ProductMedia, ProductBarcode):
    """
    Represents the final Product Response
    """

    class Config(APIModel.Config):
        ...

    # For media
    thumbnail_url: str | None
    barcode_image_url: str | None


class ProductUpdate(ProductBarcode, SequentialId):
    name: str | None
    description: str | None
    manufacturer: str | None


class ProductScrapeResult(ProductBarcode, ProductInformation):
    barcode_image: bytes | None = None
    thumbnail: bytes | None = None
