import uuid

from barcode_api.config.database import AsyncSession
from barcode_api.deps.common import DBSession
from barcode_api.models.shopping_list import ShoppingList
from barcode_api.models.shopping_list_item import ShoppingListItem
from barcode_api.schemas.shopping_list import ShoppingListCreate, ShoppingListUpdate
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .crud_service import CrudService


class ShoppingListCrud(CrudService[ShoppingList, ShoppingListCreate, ShoppingListUpdate]):
    def __init__(self, *, db_session: AsyncSession = DBSession()) -> None:
        super().__init__(model=ShoppingList, session=db_session)

    async def get_by_owner_user_id(self, owner_user_id: str) -> list[ShoppingList]:
        query = select(ShoppingList).where(self.model.owner_user_id == owner_user_id)
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def get(self, id: int | uuid.UUID) -> ShoppingList | None:
        query = select(ShoppingList).where(self.model.id == id).options(selectinload(ShoppingList.items))
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def insert_list_item(self, list_id: int, item: ShoppingListItem) -> None:
        target_list = await self.get(list_id)

        if target_list is None:
            raise ValueError(f"Shopping list with id {list_id} does not exist")

        target_list.items.append(item)
        self.db_session.add(target_list)
        await self.db_session.commit()

    async def remove(self, *, id: int) -> None:
        target_list = await self.get(id)

        if target_list is None:
            raise ValueError(f"Shopping list with id {id} does not exist")

        # Remove all items from the list
        for item in target_list.items:
            await self.db_session.delete(item)

        await self.db_session.delete(target_list)
        await self.db_session.commit()
