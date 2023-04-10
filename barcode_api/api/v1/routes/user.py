from typing import Any

from barcode_api import deps, schemas, services
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.post("/", response_model=schemas.User)
def auth_register(
    *,
    user_crud: services.UserCRUD = Depends(deps.crud.user_crud),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Register new user
    """
    user = user_crud.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.create(obj_in=user_in)
