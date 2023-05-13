from barcode_api import config, models, schemas, services
from barcode_api.deps.common import DBSession


class ScrapeResultRepository(
    services.CrudService[models.ScrapeResult, schemas.ScrapeResultCreate, schemas.ScrapeResultInDB]
):
    def __init__(self, *, db_session: config.AsyncSession = DBSession()) -> None:
        print(db_session)
        super().__init__(model=models.ScrapeResult, session=db_session)
