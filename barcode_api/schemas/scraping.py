import datetime

from barcode_api.utils.optional import make_optional
from bs4 import BeautifulSoup
from pydantic import Field, HttpUrl, validator

from .products import ProductSearch


class ScrapeResultInDB(ProductSearch):
    class Config:
        orm_mode = True

    id: int | None = None
    url: HttpUrl
    html: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    scrape_strategy: str

    @validator("html", pre=True, check_fields=False)
    def validate_html(cls, v: str) -> str:
        soup = BeautifulSoup(v, "html.parser")
        return soup.prettify()  # type: ignore


class ScrapeResultCreate(ScrapeResultInDB):
    ...


@make_optional()
class ScrapeResultUpdate(ScrapeResultInDB):
    ...
