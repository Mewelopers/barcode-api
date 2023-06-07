from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from barcode_api.config.database import Base, CreatedAtUpdatedAtMixin, UUIDMixin


class ImageData(Base, UUIDMixin, CreatedAtUpdatedAtMixin):
    """
    A model representing binary image data.

    Attributes:
        data (bytes): The binary data for the image.
    """

    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    def __repr__(self) -> str:
        return f"<ImageData id={self.id}>"
