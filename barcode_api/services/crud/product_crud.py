from barcode_api.config.database import AsyncSession
from barcode_api.deps.common import DBSession, Service
from barcode_api.models.image_data import ImageData
from barcode_api.models.product import Product
from barcode_api.schemas.products import ProductCreate, ProductUpdate
from barcode_api.services.scraping import ScrapeService
from sqlalchemy import select

from .crud_service import CrudService


class ProductCrud(CrudService[Product, ProductCreate, ProductUpdate]):
    def __init__(
        self, *, db_session: AsyncSession = DBSession(), scrape_service: ScrapeService = Service(ScrapeService)
    ) -> None:
        super().__init__(model=Product, session=db_session)
        self.scrape_service = scrape_service

    async def get_by_barcode(self, barcode: str) -> Product | None:
        """
        Get a single object by barcode
        """
        stmt = select(self.model).where(self.model.barcode == barcode)
        return await self.db_session.scalar(stmt)

    async def create(self, *, obj_in: ProductCreate) -> Product:
        if obj_in.thumbnail is not None:
            thumbnail = ImageData(data=obj_in.thumbnail)
        else:
            thumbnail = None

        if obj_in.barcode_image is not None:
            barcode_image = ImageData(data=obj_in.barcode_image)
        else:
            barcode_image = None

        db_obj = Product(
            barcode=obj_in.barcode,
            name=obj_in.name,
            thumbnail=thumbnail,
            barcode_image=barcode_image,
            manufacturer=obj_in.manufacturer,
            description=obj_in.description,
        )

        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def find_online(self, barcode: str) -> Product | None:
        res = await self.get_by_barcode(barcode)

        if res is not None:
            return res

        async with self.scrape_service as scrape_service:
            scrape_data = await scrape_service.scrape(barcode)
            obj = await self.create(obj_in=scrape_data)
            return obj
