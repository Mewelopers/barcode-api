import datetime

from pydantic import BaseModel


class CreatedAtUpdatedAt(BaseModel):
    """
    Base class for models that have created_at and updated_at fields
    """

    class Config:
        orm_mode = True

    created_at: datetime.datetime
    updated_at: datetime.datetime


class SequentialId(BaseModel):
    """
    Base class for models that have an id field

    """

    class Config:
        orm_mode = True

    id: int
