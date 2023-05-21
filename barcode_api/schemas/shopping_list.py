from __future__ import annotations

from barcode_api.utils.optional import make_optional
from pydantic import BaseModel

from .db_base import TrackedDbSchema


class ShoppingListCreateRequest(BaseModel):
    list_title: str


class SHoppingListUpdateRequest(ShoppingListCreateRequest):
    pass


class ShoppingListCreate(BaseModel):
    owner_user_id: str
    list_title: str


@make_optional(exclude=["id"])
class ShoppingListUpdate(ShoppingListCreate):
    id: int


class ShoppingListInDb(TrackedDbSchema, ShoppingListCreate):
    id: int
    items: "list[ShoppingListItemInDb]"


class ShoppingListResponse(TrackedDbSchema, ShoppingListCreate):
    class Config:
        orm_mode = True

    id: int


from .shopping_list_item import ShoppingListItemInDb  # noqa: E402

ShoppingListItemInDb.update_forward_refs()
