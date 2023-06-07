from abc import ABC
from typing import Any, Dict, Generic, Sequence, Type, TypeVar, cast

from pydantic import BaseModel, UUID4
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

from barcode_api.config.database import AsyncSession, Base, SequentialIdMixin, UUIDMixin

# This typing is not fully correct, however at this point I'm not soure if there is a better way
# What is needed here is to say that the ModelType is a subclass of of Model which inherits from Base
# and has either SequentialIdMixin or UUIDMixin applied to it as a form of multiple inheritance
# it would be possible if there would be a Intersection type in python
# see: https://github.com/python/typing/issues/18
# From research it seems like the Protocol structual typing would work, however it is too much work
# in order to get the Protocol type to work with sqlalchemy models it would have to define the interface
# that sqlalchemy has and that would be a lot of work
# You cannot inherit from sqlalchemy models in order to define the protocol
# Please contact me if you have a better solution I would love to hear it
ModelType = TypeVar("ModelType", bound=SequentialIdMixin | UUIDMixin)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CrudService(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """
    Base class for CRUD services.

    This class implements basic CRUD operations for a model.

    Args:
        model (Type[ModelType]): The SQLAlchemy model to perform CRUD operations on.
        session (AsyncSession): The async SQLAlchemy session to use for database operations.

    Attributes:
        model (Type[ModelType]): The SQLAlchemy model to perform CRUD operations on.
        db_session (AsyncSession): The async SQLAlchemy session to use for database operations.

    Example:
        from barcode_api.config.database import AsyncSession, Base, SequentialIdMixin
        from pydantic import BaseModel
        from typing import Type

        class MyModel(Base, SequentialIdMixin):
            ...

        class MyService(CrudService[MyModel, BaseModel, BaseModel]):
            def __init__(self, session: AsyncSession):
                super().__init__(model=MyModel, session=session)

            async def create(self, obj_in: BaseModel) -> MyModel:
                ...

            async def update(self, obj: MyModel, obj_in: BaseModel) -> MyModel:
                ...

            async def delete(self, obj: MyModel) -> None:
                ...

            async def get_multi_by_name(self, name: str) -> list[MyModel]:
                ...
    """

    def __init__(self, *, model: Type[ModelType], session: AsyncSession) -> None:
        """
        Initialize a new instance of the CrudService class.

        Args:
            model (Type[ModelType]): The SQLAlchemy model to perform CRUD operations on.
            session (AsyncSession): The async SQLAlchemy session to use for database operations.
        """
        self.model = model
        self.db_session = session

    async def get(self, id: int | UUID4) -> ModelType | None:
        """
        Get a single object by id.

        Args:
            id (int | UUID4): The id of the object to retrieve.

        Returns:
            ModelType | None: The retrieved object, or None if it does not exist.

        Raises:
            ValueError: If the id is not a valid integer or UUID4 string.
        """
        stmt = select(self.model).where(self.model.id == id)
        return await self.db_session.scalar(stmt)

    async def get_multi(self, *, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """
        Get multiple objects with optional pagination.

        Args:
            skip (int): The number of objects to skip. Default is 0.
            limit (int): The maximum number of objects to retrieve. Default is 100.

        Returns:
            Sequence[ModelType]: A sequence of retrieved objects.

        Example:
            # Retrieve the first 10 objects
            objects = await service.get_multi(limit=10)

            # Retrieve the next 10 objects
            objects = await service.get_multi(skip=10, limit=10)
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db_session.scalars(stmt)
        return result.all()

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new object using provided schema object.

        Args:
            obj_in (CreateSchemaType): The Pydantic schema object to create the new object from.

        Returns:
            ModelType: The created object.

        Example:
            # Create a new object
            obj_in = MyCreateSchema(...)
            obj = await service.create(obj_in=obj_in)
        """
        # Currently there is no intersectioon type in python
        # meaning thet we cannot say the following
        # The ModelType is either SequentialIdMixin or UUIDMixin
        # however it always inherits from Base
        # so we have to cast it to Base
        db_obj = cast(Type[Base], self.model)(**obj_in.dict())

        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return cast(ModelType, db_obj)

    async def update(self, *, db_obj: ModelType, obj_in: UpdateSchemaType | Dict[str, Any]) -> ModelType:
        """
        Update an existing object using provided schema object or dict.

        Args:
            db_obj (ModelType): The object to update.
            obj_in (UpdateSchemaType | Dict[str, Any]): The Pydantic schema object or dict to update the object from.

        Returns:
            ModelType: The updated object.

        Example:
            # Update an existing object
            obj_in = MyUpdateSchema(...)
            obj = await service.update(db_obj=obj, obj_in=obj_in)
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
        Remove an object by id.

        Args:
            id (int): The id of the object to remove.

        Returns:
            ModelType | None: The removed object, or None if it does not exist.

        Raises:
            ValueError: If the id is not a valid integer.
        """
        stmt = select(self.model).where(self.model.id == id)
        obj = await self.db_session.scalar(stmt)
        await self.db_session.delete(obj)
        await self.db_session.commit()
        return obj
