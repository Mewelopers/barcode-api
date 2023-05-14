import barcode
from pydantic import BaseModel, Field, validator


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
