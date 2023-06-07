from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from barcode_api.config.database import Base, SequentialIdMixin, CreatedAtUpdatedAtMixin


class ScrapeData(Base, SequentialIdMixin, CreatedAtUpdatedAtMixin):
    """
    A model representing scraped data.

    Attributes:
        id (int): The unique identifier for the scraped data.
        barcode (str): The barcode of the product associated with the scraped data.
        url (str): The URL from which the data was scraped.
        html (str): The HTML content of the page from which the data was scraped
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    barcode: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    html: Mapped[str] = mapped_column(Text, nullable=False)
