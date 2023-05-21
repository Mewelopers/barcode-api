import typing
from typing import List

from barcode_api.config.database import Base, SequentialIdMixin, TrackedMixin
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if typing.TYPE_CHECKING:
    from .shopping_list_item import ShoppingListItem


class ShoppingList(Base, SequentialIdMixin, TrackedMixin):
    """
    A model representing a shopping list.

    Attributes:
        owner_user_id (int): The ID of the user who owns the shopping list.
        list_title (str): The title of the shopping list.
        items (List[ShoppingListItem]): The list of items in the shopping list.
    """

    owner_user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    list_title: Mapped[str] = mapped_column(String(255), nullable=False)

    items: Mapped[List["ShoppingListItem"]] = relationship("ShoppingListItem", back_populates="list")

    def __repr__(self) -> str:
        return f"<ShoppingList id={self.id} owner_user_id={self.owner_user_id} list_title={self.list_title}>"
