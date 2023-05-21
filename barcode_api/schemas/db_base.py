import datetime

from pydantic import BaseModel


class TrackedDbSchema(BaseModel):
    created_at: datetime.datetime
    updated_at: datetime.datetime
