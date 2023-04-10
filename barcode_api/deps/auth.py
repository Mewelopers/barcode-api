from barcode_api import config, models, schemas, services
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

from . import common, crud, inject

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{config.settings.API_V1_STR}/auth/access-token"
)


def get_current_user(
    settings: common.Settings = Depends(common.get_settings),
    jwt_service: services.JwtService = Depends(inject.jwt_service),
    user_crud: services.UserCRUD = Depends(crud.user_crud),
    token: str = Depends(oauth2_scheme),
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[jwt_service.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(status_code=404, detail="User not found")
    user = user_crud.get(id=token_data.subject)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
