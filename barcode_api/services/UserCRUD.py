from datetime import datetime
from typing import Any, Dict

from barcode_api.config.settings import Settings
from sqlalchemy.orm import Session

from ..models import User
from ..schemas.user import UserCreate, UserUpdate
from .mixin.base import AppCrudService
from .mixin.security import SecurityMixin


class UserCRUD(AppCrudService[User, UserCreate, UserUpdate], SecurityMixin):
    def __init__(self, db: Session, config: Settings):
        super().__init__(model=User, db=db, config=config)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            password=self.get_password_hash(obj_in.password),
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, *, db_obj: User, obj_in: UserUpdate | Dict[str, Any]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if update_data.get("password"):
            hashed_password = self.get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["password"] = hashed_password
        update_data["last_updated"] = datetime.now()
        return super().update(db_obj=db_obj, obj_in=update_data)

    def authenticate(self, *, email: str, password: str) -> User | None:
        user = self.get_by_email(email=email)
        if not user:
            return None
        if not self.verify_password(password, user.password):
            return None
        return user

    @staticmethod
    def is_active(user: User) -> bool:
        return user.is_active
