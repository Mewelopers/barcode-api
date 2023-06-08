import logging
from typing import Sequence

from sqlalchemy import select

from barcode_api.config.database import AsyncSession
from barcode_api.deps.common import DBSession, Service
from barcode_api.models.product import Product
from barcode_api.schemas.products import ProductCreate, ProductUpdate
from barcode_api.schemas.image_data import ImageDataCreate
from barcode_api.services.scraping import ScrapeService
from barcode_api.services.scraping.exceptions import ParserException
from barcode_api.services.crud.image_crud import ImageDataCrud

from .crud_service import CrudService

logger = logging.getLogger(__name__)


class ProductCrud(CrudService[Product, ProductCreate, ProductUpdate]):
    """
    This class provides CRUD (Create, Read, Update, Delete) operations for the `Product` model.
    """

    def __init__(
        self,
        *,
        db_session: AsyncSession = DBSession(),
        scrape_service: ScrapeService = Service(ScrapeService),
        image_crud: ImageDataCrud = Service(ImageDataCrud),
    ) -> None:
        """
        Initializes the `CrudService` with the `Product` model and the `db_session` parameter.
        It also takes in an optional `scrape_service` parameter which is an instance of `ScrapeService` and
        defaults to `Service(ScrapeService)`.

        Args:
            db_session (AsyncSession, optional): An instance of `AsyncSession` that represents the database session.

            scrape_service (ScrapeService, optional): An instance of `ScrapeService`.

        Returns:
            None
        """
        super().__init__(model=Product, session=db_session)
        self.scrape_service = scrape_service
        self.image_crud = image_crud

    async def get_by_barcode(self, barcode: str) -> Product | None:
        """
        Get a single object by barcode.

        Args:
            barcode (str): The barcode of the product to retrieve.

        Returns:
            Product | None: The product with the given barcode, or None if it does not exist.
        """
        stmt = select(self.model).where(self.model.barcode == barcode)
        return await self.db_session.scalar(stmt)

    async def create(self, *, obj_in: ProductCreate) -> Product:
        """
        Get a single object by barcode.

        Args:
            barcode (str): The barcode of the product to retrieve.

        Returns:
            Product | None: The product with the given barcode, or None if it does not exist.
        """

        db_obj = Product(
            barcode=obj_in.barcode,
            name=obj_in.name,
            manufacturer=obj_in.manufacturer,
            description=obj_in.description,
        )

        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def find_online(self, barcode: str) -> Product | None:
        """
        Get a single object by barcode.

        Args:
            barcode (str): The barcode of the product to retrieve.

        Returns:
            Product | None: The product with the given barcode, or None if it does not exist.
        """
        res = await self.get_by_barcode(barcode)

        if res is not None:
            return res

        async with self.scrape_service as scrape_service:
            try:
                scrape_data = await scrape_service.scrape(barcode)
            except ParserException as e:
                logging.info(f"Error scraping barcode: {barcode}, error: %s", e)
                return None

        product = await self.create(obj_in=ProductCreate.from_orm(scrape_data))

        if scrape_data.barcode_image is not None:
            barcode_image = await self.image_crud.create(obj_in=ImageDataCreate(data=scrape_data.barcode_image))
            product.barcode_image = barcode_image

        if scrape_data.thumbnail is not None:
            thumbnail = await self.image_crud.create(obj_in=ImageDataCreate(data=scrape_data.thumbnail))
            product.thumbnail = thumbnail

        self.db_session.add(product)
        await self.db_session.commit()
        await self.db_session.refresh(product)
        return product

    async def search(self, search: str, *, limit: int) -> Sequence[Product]:
        query = select(self.model).where(self.model.name.ilike(f"%{search}%")).limit(limit)

        return (await self.db_session.execute(query)).scalars().all()
