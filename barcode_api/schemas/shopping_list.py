from pydantic import BaseModel
from fastapi_utils.api_model import APIModel
from .db_base import CreatedAtUpdatedAt, SequentialId


class ShoppingListBody(APIModel):
    """
    Schema representing API request and response bodies for shopping lists.
    """

    list_title: str


class ShoppingListResponse(ShoppingListBody, SequentialId, CreatedAtUpdatedAt):
    """
    Schema representing a shopping list in the API.
    """

    class Config(APIModel.Config):
        ...

    owner_user_id: str


class ShoppingListCreate(BaseModel):
    """
    Schema for creating new shopping lists.
    """

    class Config:
        orm_mode = True

    owner_user_id: str
    list_title: str


class ShoppingListUpdate(SequentialId):
    """
    Schema for updating existing shopping lists
    """

    class Config:
        orm_mode = True

    owner_user_id: str | None = None
    list_title: str | None = None
