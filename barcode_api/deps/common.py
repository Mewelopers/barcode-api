from typing import Any, Callable, Optional

from barcode_api.config import database
from fastapi import params


def Service(service: Optional[Callable[..., Any]] = None) -> Any:
    return params.Depends(service)


def DBSession() -> Any:
    """
    Dependency for getting a database session.
    """
    return params.Depends(database.db_session)
