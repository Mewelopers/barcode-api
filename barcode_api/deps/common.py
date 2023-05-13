from typing import Any

from barcode_api.config import database
from fastapi import params


def DBSession() -> Any:
    """
    Dependency for getting a database session.
    """
    return params.Depends(database.db_session)
