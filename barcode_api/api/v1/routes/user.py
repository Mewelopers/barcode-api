from fastapi import APIRouter

from barcode_api.deps.auth import JKPBasicAuth, JKPUserInfo
from barcode_api.schemas import OIDCToken, User

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/me", response_model=User)
def get_user_info(
    user: User = JKPUserInfo(),
) -> User:
    """
    Retrives the user info for the current user
    """
    return user


@router.get("/token", response_model=OIDCToken)
def get_user_token(
    token: OIDCToken = JKPBasicAuth(),
) -> OIDCToken:
    """
    Retrives the pared token for the current user
    """
    return token
