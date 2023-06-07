from barcode_api.config.database import AsyncSession
from barcode_api.deps.common import DBSession
from barcode_api.models.image_data import ImageData
from barcode_api.schemas.image_data import ImageDataCreate, ImageDataUpdate

from .crud_service import CrudService


class ImageDataCrud(CrudService[ImageData, ImageDataCreate, ImageDataUpdate]):
    """
    This class provides CRUD (Create, Read, Update, Delete) operations for the `ImageData` model.
    """

    def __init__(self, *, db_session: AsyncSession = DBSession()) -> None:
        """
        Initializes the `CrudService` with the `ImageData` model and the `db_session` parameter.

        Args:
            db_session (AsyncSession, optional): An instance of `AsyncSession`. Defaults to `DBSession()`.

        Returns:
            None
        """
        super().__init__(model=ImageData, session=db_session)
