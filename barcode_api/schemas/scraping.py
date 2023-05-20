from barcode_api.utils.optional import make_optional
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, validator

from .db_base import TrackedDbSchema


class ScrapeDataCreate(BaseModel):
    barcode: str = Field(..., min_length=8, max_length=14, regex=r"^[0-9]+$")
    url: str
    html: str

    @validator("html", pre=True, check_fields=False)
    def validate_html(cls, v: str) -> str:
        soup = BeautifulSoup(v, "html.parser")
        return soup.prettify()  # type: ignore


class ScrapeDataInDB(ScrapeDataCreate, TrackedDbSchema):
    class Config:
        orm_mode = True

    id: int


@make_optional(exclude=["id"])
class ScrapeDataUpdate(ScrapeDataInDB):
    ...
