import datetime

from barcode_api.config.database import Base
from sqlalchemy import TIMESTAMP, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column


class ScrapeResult(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    barcode: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    url: Mapped[str] = mapped_column(String(512), nullable=False)

    timestamp: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    html: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<ScrapeResult(barcode={self.barcode}, url={self.url}, timestamp={self.timestamp})>"
