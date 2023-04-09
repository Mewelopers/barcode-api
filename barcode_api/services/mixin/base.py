from typing import Any, Dict, Generic, Type, TypeVar

from barcode_api.config.database import Base
from barcode_api.config.settings import Settings
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session


class DBSessionMixin:
    def __init__(self, db: Session, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.db = db


class AppSettingsMixin:
    def __init__(self, config: Settings, *args: Any, **kwargs: Any) -> None:
        self.config = config


class AppService(DBSessionMixin, AppSettingsMixin):
    pass


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class AppCrudService(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType],
    DBSessionMixin,
    AppSettingsMixin,
):
    def __init__(self, model: Type[ModelType], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.model = model

    def get(self, id: int) -> ModelType | None:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        self, *, db_obj: ModelType, obj_in: UpdateSchemaType | Dict[str, Any]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, *, id: int) -> ModelType | None:
        obj = self.db.query(self.model).get(id)
        self.db.delete(obj)
        self.db.commit()
        return obj