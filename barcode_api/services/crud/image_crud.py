from barcode_api.config.database import AsyncSession
from barcode_api.deps.common import DBSession
from barcode_api.models.image_data import ImageData
from barcode_api.schemas.image_data import ImageDataCreate, ImageDataUpdate

from .crud_service import CrudService


class ImageDataCrud(CrudService[ImageData, ImageDataCreate, ImageDataUpdate]):
    def __init__(self, *, db_session: AsyncSession = DBSession()) -> None:
        super().__init__(model=ImageData, session=db_session)
