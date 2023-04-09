from functools import lru_cache
from typing import Generator

from barcode_api.config import Settings
from barcode_api.config.database import SessionLocal
from sqlalchemy.orm import Session


def get_db() -> Generator[Session, None, None]:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@lru_cache()
def get_settings() -> Settings:
    return Settings()
