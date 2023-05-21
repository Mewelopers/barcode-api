import datetime

from pydantic import BaseModel


class TrackedDbSchema(BaseModel):
    class Config:
        orm_mode = True

    created_at: datetime.datetime
    updated_at: datetime.datetime
