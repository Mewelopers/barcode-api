import typing
import uuid
from typing import Optional

from barcode_api.config.database import Base, SequentialIdMixin, CreatedAtUpdatedAtMixin
from sqlalchemy import TEXT, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if typing.TYPE_CHECKING:
    from .image_data import ImageData


class Product(Base, SequentialIdMixin, CreatedAtUpdatedAtMixin):
    """
    A model representing a product.

    Attributes:
        name (str): The name of the product.
        description (str): The description of the product.
        manufacturer (str): The manufacturer of the product.
        barcode (str): The barcode of the product.
        thumbnail_uuid (uuid.UUID): The unique identifier of the thumbnail image for the product.
        thumbnail (ImageData): The thumbnail image for the product.
        barcode_image_uuid (uuid.UUID): The unique identifier of the barcode image for the product.
        barcode_image (ImageData): The barcode image for the product.
    """

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(TEXT, nullable=True)
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=True)
    barcode: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    thumbnail_uuid: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ImageData.id"), nullable=True, unique=True)
    thumbnail: Mapped[Optional["ImageData"]] = relationship(
        "ImageData", foreign_keys=[thumbnail_uuid], uselist=False, cascade="all, delete"
    )

    barcode_image_uuid: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("ImageData.id"), nullable=True, unique=True
    )
    barcode_image: Mapped[Optional["ImageData"]] = relationship(
        "ImageData", foreign_keys=[barcode_image_uuid], uselist=False, cascade="all, delete"
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name} manufacturer={self.manufacturer} barcode={self.barcode}>"
