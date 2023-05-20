import datetime
import uuid
from typing import AsyncGenerator

from barcode_api.config.settings import settings
from sqlalchemy import TIMESTAMP, UUID, func, text
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__


class SequentialIdMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"), unique=True, nullable=False
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


class TrackedMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    future=True,
    echo=False,
    pool_size=10,
    max_overflow=10,
    isolation_level="AUTOCOMMIT",
)


AsyncDBSession = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncDBSession() as session:
        yield session
