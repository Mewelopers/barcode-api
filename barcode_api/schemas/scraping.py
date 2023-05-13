import datetime

import barcode
from barcode_api.utils.optional import make_optional
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, HttpUrl, constr, validator


class ScrapeResultCreate(BaseModel):
    barcode: constr(min_length=1, max_length=32, regex=r"^[0-9]+$")  # type: ignore

    @validator("barcode")
    def validate_barcode(cls, v: str) -> str:
        barcode_type = len(v)

        match barcode_type:
            case 8:
                checker = barcode.EAN8
            case 13:
                checker = barcode.EAN13
            case 14:
                checker = barcode.EAN14
            case _:
                raise ValueError("Invalid barcode length")

        return checker(v).get_fullcode()  # type: ignore


class ScrapeResultInDB(ScrapeResultCreate):
    class Config:
        orm_mode = True

    id: int | None = None
    barcode: constr(min_length=1, max_length=32, regex=r"^[0-9]+$")  # type: ignore
    url: HttpUrl
    html: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)

    @validator("barcode")
    def validate_url(cls, v: str) -> str:
        barcode_type = len(v)

        match barcode_type:
            case 8:
                checker = barcode.EAN8
            case 13:
                checker = barcode.EAN13
            case 14:
                checker = barcode.EAN14
            case _:
                raise ValueError("Invalid barcode length")

        return checker(v).get_fullcode()  # type: ignore

    @validator("html", pre=True, check_fields=False)
    def validate_html(cls, v: str) -> str:
        soup = BeautifulSoup(v, "html.parser")
        return soup.prettify()  # type: ignore


@make_optional()
class ScrapeResultUpdate(ScrapeResultInDB):
    ...
