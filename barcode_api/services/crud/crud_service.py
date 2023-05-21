from abc import ABC
from typing import Any, Dict, Generic, Sequence, Type, TypeVar, cast

from barcode_api.config.database import AsyncSession, Base, SequentialIdMixin, UUIDMixin
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select

ModelType = TypeVar("ModelType", bound=SequentialIdMixin | UUIDMixin)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CrudService(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """
    Base class for CRUD services
    This class implements basic CRUD operations for a model
    """

    def __init__(self, *, model: Type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.db_session = session

    async def get(self, id: int | str) -> ModelType | None:
        """
        Get a single object by id, can be a numeric id or a UUID string
        """
        stmt = select(self.model).where(self.model.id == id)
        return await self.db_session.scalar(stmt)

    async def get_multi(self, *, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """
        Get multiple objects with optional pagination
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db_session.scalars(stmt)
        return result.all()

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new object using provided schema object
        """
        obj_in_data = jsonable_encoder(obj_in)

        # Currently there is no intersectioon type in python
        # meaning thet we cannot say the following
        # The ModelType is either SequentialIdMixin or UUIDMixin
        # however it always inherits from Base
        # so we have to cast it to Base
        db_obj = cast(Type[Base], self.model)(**obj_in_data)

        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return cast(ModelType, db_obj)

    async def update(self, *, db_obj: ModelType, obj_in: UpdateSchemaType | Dict[str, Any]) -> ModelType:
        """
        Update an existing object using provided schema object or dict
        """
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def remove(self, *, id: int) -> ModelType | None:
        """
        Remove an object by id
        """
        stmt = select(self.model).where(self.model.id == id)
        obj = await self.db_session.scalar(stmt)
        await self.db_session.delete(obj)
        await self.db_session.commit()
        return obj
