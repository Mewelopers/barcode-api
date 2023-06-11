from barcode_api.config.database import AsyncSession
from barcode_api.deps.common import DBSession
from barcode_api.models.shopping_list_item import ShoppingListItem
from barcode_api.schemas.shopping_list_item import ShoppingListItemCreate, ShoppingListItemUpdate
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .crud_service import CrudService


class ShoppingListItemCrud(CrudService[ShoppingListItem, ShoppingListItemCreate, ShoppingListItemUpdate]):
    def __init__(self, *, db_session: AsyncSession = DBSession()) -> None:
        super().__init__(model=ShoppingListItem, session=db_session)

    async def get_items_by_list_id(self, *, list_id: int) -> list[ShoppingListItem]:
        query = (
            select(ShoppingListItem)
            .where(self.model.list_id == list_id)
            .options(selectinload(ShoppingListItem.product))
        )
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def get_item_from_list(self, *, item_id: int) -> ShoppingListItem | None:
        query = (
            select(ShoppingListItem)
            .where(self.model.id == item_id)
            .options(selectinload(ShoppingListItem.list))
            .options(selectinload(ShoppingListItem.product))
        )
        return (await self.db_session.execute(query)).scalar()
