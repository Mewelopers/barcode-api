from datetime import datetime, timedelta
from typing import Any

from barcode_api.config.settings import Settings
from barcode_api.services.mixin.base import AppService
from jose import jwt
from sqlalchemy.orm import Session

from .mixin.security import SecurityMixin


class JwtService(AppService, SecurityMixin):
    ALGORITHM = "HS256"

    def __init__(self, db: Session, config: Settings):
        super().__init__(db=db, config=config)

    def create_access_token(
        self, subject: str | Any, expires_delta: timedelta | None = None
    ) -> str:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        jwt_payload = {"expires": expire, "subject": str(subject)}
        encoded_jwt = jwt.encode(
            jwt_payload, self.config.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_jwt
