import uuid

from barcode_api.utils.optional import make_optional

from .db_base import TrackedDbSchema


class ImageDataInDb(TrackedDbSchema):
    class Config:
        orm_mode = True

    id: uuid.UUID
    data: bytes


class ImageDataCreate(ImageDataInDb):
    pass


@make_optional(exclude=["id"])
class ImageDataUpdate(ImageDataInDb):
    pass
