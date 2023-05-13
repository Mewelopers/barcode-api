from typing import AsyncGenerator

from barcode_api.config.settings import settings
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__


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
