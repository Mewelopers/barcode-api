from barcode_api.deps.auth import JKPBasicAuth, JKPUserInfo
from barcode_api.schemas import OIDCToken, User
from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=User)
def get_user_info(
    user: User = JKPUserInfo(),
) -> User:
    return user


@router.get("/token", response_model=OIDCToken)
def get_user_token(
    token: OIDCToken = JKPBasicAuth(),
) -> OIDCToken:
    return token
