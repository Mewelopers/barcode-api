from datetime import timedelta
from typing import Any

from barcode_api import config, deps, models, schemas, services
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/auth/access-token", response_model=schemas.Token)
def auth_access_token(
    user_crud: services.UserCRUD = Depends(deps.crud.user_crud),
    jwt_service: services.JwtService = Depends(deps.inject.jwt_service),
    form_data: OAuth2PasswordRequestForm = Depends(),
    settings: config.Settings = Depends(deps.common.get_settings),
) -> Any:
    user = user_crud.authenticate(email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password",
        )
    elif not user_crud.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return schemas.Token(
        access_token=jwt_service.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        token_type="bearer",
    )


@router.get("/auth/me", response_model=schemas.User)
def return_me(
    user: models.User = Depends(deps.auth.get_current_user),
) -> Any:
    return user
