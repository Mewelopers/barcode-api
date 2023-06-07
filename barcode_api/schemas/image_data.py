from pydantic import BaseModel, UUID4

from .db_base import CreatedAtUpdatedAt


class ImageDataInDb(CreatedAtUpdatedAt):
    """Represents the ImageData object in the database.

    Args:
        TrackedDbSchema (_type_): _description_
    """

    id: UUID4
    data: bytes


class ImageDataCreate(BaseModel):
    """Schema for creating an ImageData object."""

    data: bytes


class ImageDataUpdate(BaseModel):
    """Schema for updating an ImageData object."""

    data: bytes
