# isort:skip_file.
from __future__ import annotations

import barcode  # type: ignore
from pydantic import BaseModel, validator

from .db_base import TrackedDbSchema
from .products import ProductInDb


class ShoppingListItemCreate(BaseModel):
    product_id: int | None
    name: str
    list_id: int


class ShoppingListItemCreateRequest(BaseModel):
    name: str
    barcode: str | None

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

        if v != checker(v).get_fullcode():
            raise ValueError("Invalid barcode")

        return checker(v).get_fullcode()  # type: ignore


class ShoppingListItemUpdate(BaseModel):
    product_id: int | None
    name: str
    list_id: int


class ShoppingListItemInDb(TrackedDbSchema, ShoppingListItemCreate):
    id: int
    list_id: int
    product_id: int | None
    list: "ShoppingListInDb"
    product: ProductInDb | None


class ShoppingListItemResponse(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: str
    list_id: int
    product_barcode: str | None


# This prevents a circular import
from .shopping_list import ShoppingListInDb  # noqa: E402

ShoppingListItemInDb.update_forward_refs()
