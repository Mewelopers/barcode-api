from pydantic import BaseModel

from .auth import AuthRole


class User(BaseModel):
    id: str
    name: str
    email: str
    roles: set[AuthRole]
