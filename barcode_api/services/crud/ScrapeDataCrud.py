from barcode_api.config.database import AsyncSession
from barcode_api.deps.common import DBSession
from barcode_api.models import ScrapeData
from barcode_api.schemas.scraping import ScrapeDataCreate, ScrapeDataUpdate
from sqlalchemy import select

from .CrudService import CrudService


class ScrapeDataCrud(CrudService[ScrapeData, ScrapeDataCreate, ScrapeDataUpdate]):
    def __init__(self, *, db_session: AsyncSession = DBSession()) -> None:
        super().__init__(model=ScrapeData, session=db_session)

    async def get_by_barcode(self, barcode: str) -> ScrapeData | None:
        """
        Get a single object by barcode
        """
        stmt = select(self.model).where(self.model.barcode == barcode)
        return await self.db_session.scalar(stmt)
