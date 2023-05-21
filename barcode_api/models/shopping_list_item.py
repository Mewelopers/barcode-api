import typing

from barcode_api.config.database import Base, SequentialIdMixin, TrackedMixin
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if typing.TYPE_CHECKING:
    from .shopping_list import ShoppingList
    from .product import Product


class ShoppingListItem(Base, SequentialIdMixin, TrackedMixin):
    """
    A model representing an item in a shopping list.

    Attributes:
        name (str): The name of the shopping list item.
        list_id (str): The ID of the shopping list that the item belongs to.
        list (ShoppingList): The shopping list that the item belongs to.
        product_id (str): The ID of the product associated with the shopping list item.
        product (Product): The product associated with the shopping list item.
    """

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    list_id: Mapped[int] = mapped_column(ForeignKey("ShoppingList.id"), nullable=False)
    list: Mapped["ShoppingList"] = relationship(
        "ShoppingList", foreign_keys=[list_id], uselist=False, back_populates="items"
    )

    product_id: Mapped[str] = mapped_column(ForeignKey("Product.id"), nullable=True)
    product: Mapped["Product"] = relationship("Product", foreign_keys=[product_id], uselist=False)

    def __repr__(self) -> str:
        return f"<ShoppingListItem id={self.id} name={self.name} list_id={self.list_id} product_id={self.product_id}>"
