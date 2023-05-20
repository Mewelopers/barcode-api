from barcode_api.config.database import AsyncSession
from barcode_api.deps.common import DBSession
from barcode_api.models import Product
from barcode_api.schemas.products import ProductCreate, ProductUpdate
from sqlalchemy import select

from .CrudService import CrudService


class ProductCrud(CrudService[Product, ProductCreate, ProductUpdate]):
    def __init__(self, *, db_session: AsyncSession = DBSession()) -> None:
        super().__init__(model=Product, session=db_session)

    async def get_by_barcode(self, barcode: str) -> Product | None:
        """
        Get a single object by barcode
        """
        stmt = select(self.model).where(self.model.barcode == barcode)
        return await self.db_session.scalar(stmt)

    async def find_online(self, barcode: str) -> Product | None:
        raise NotImplementedError()
