from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr | None = None


class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=32)


class UserUpdate(UserBase):
    password: str | None = None


class UserInDBBase(UserBase):
    id: int | None = None
    is_active: bool | None = True
    last_updated: datetime | None = None

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    password: str
