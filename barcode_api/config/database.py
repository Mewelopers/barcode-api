import sqlalchemy as sa
from barcode_api.config import settings
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id = sa.Column(sa.Integer, primary_key=True)
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


engine = sa.create_engine(
    settings.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)

SessionLocal = sa.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
