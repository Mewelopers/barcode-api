from pydantic import BaseModel

from .db_base import CreatedAtUpdatedAt, SequentialId


class ShoppingListBody(BaseModel):
    """
    Schema representing API request and response bodies for shopping lists.
    """

    list_title: str


class ShoppingListCreate(BaseModel):
    """
    Schema for creating new shopping lists.
    """

    class Config:
        orm_mode = True

    owner_user_id: str
    list_title: str


class ShoppingListInDb(SequentialId, CreatedAtUpdatedAt, ShoppingListCreate):
    """
    Schema representing a shopping list in the database.
    """

    class Config:
        orm_mode = True


class ShoppingListUpdate(SequentialId):
    """
    Schema for updating existing shopping lists
    """

    class Config:
        orm_mode = True

    owner_user_id: str | None = None
    list_title: str | None = None


class ShoppingListResponse(SequentialId, CreatedAtUpdatedAt, ShoppingListBody):
    """
    Schema representing a shopping list in the API.
    """

    class Config:
        orm_mode = True
