import typing
import uuid

from barcode_api.config.database import Base, SequentialIdMixin, TrackedMixin
from sqlalchemy import TEXT, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if typing.TYPE_CHECKING:
    from .ImageData import ImageData


class Product(Base, SequentialIdMixin, TrackedMixin):
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
    decription: Mapped[str] = mapped_column(TEXT, nullable=True)
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=True)
    barcode: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    thumbnail_uuid: Mapped[uuid.UUID] = mapped_column(ForeignKey("ImageData.id"), nullable=True)
    thumbnail: Mapped["ImageData"] = relationship("ImageData", foreign_keys=[thumbnail_uuid], uselist=False)

    barcode_image_uuid: Mapped[uuid.UUID] = mapped_column(ForeignKey("ImageData.id"), nullable=True)
    barcode_image: Mapped["ImageData"] = relationship("ImageData", foreign_keys=[barcode_image_uuid], uselist=False)

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name} manufacturer={self.manufacturer} barcode={self.barcode}>"
