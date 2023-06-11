from pydantic import BaseModel

from .db_base import CreatedAtUpdatedAt, SequentialId
from .products import ProductBarcode

from barcode_api.utils.optional import make_optional
from fastapi_utils.api_model import APIModel


class ShoppingListItemCreate(BaseModel):
    """
    Schema for creating a shopping list item.
    """

    class Config:
        orm_mode = True

    product_id: int | None
    name: str
    list_id: int


class ShoppingListItemInDb(SequentialId, CreatedAtUpdatedAt, ShoppingListItemCreate):
    class Config:
        orm_mode = True

    ...


@make_optional(exclude=["id"])
class ShoppingListItemUpdate(ShoppingListItemInDb):
    """
    Schema for updating a shopping list item.

    """

    ...


@make_optional(include=["barcode"])
class ShoppingListItemBody(ProductBarcode, APIModel):
    """
    Represents a shopping list item in a request body.
    """

    name: str


class ShoppingListItemResponse(ShoppingListItemInDb, APIModel):
    """
    Schema for a shopping list item response.
    """

    product_barcode: str | None
    thumbnail_url: str | None
    barcode_image_url: str | None
