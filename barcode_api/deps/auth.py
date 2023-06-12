from typing import Any

from barcode_api.config.settings import settings
from barcode_api.schemas import AuthRole, AuthScopes, OIDCToken, User
from fastapi import Depends, HTTPException, params, status
from fastapi.security import SecurityScopes
from fastapi_oidc import get_auth  # type: ignore

authenticate_user = get_auth(
    client_id=settings.OIDC_CLIENT_ID,
    base_authorization_server_uri=settings.OIDC_BASE_AUTHORIZATION_SERVER_URI,
    issuer=settings.OIDC_ISSUER,
    signature_cache_ttl=settings.OIDC_SIGNATURE_CACHE_TTL,
    token_type=OIDCToken,
    jwt_decode_options={
        "leeway": settings.OIDC_JWT_LEEWAY,
    },
)


def authenticate_user_with_scope(
    scopes: SecurityScopes,
    token: OIDCToken = Depends(authenticate_user),
) -> OIDCToken:
    """
    Requires all the scopes to be present on the token.
    In order to be authorized to access the API.
    """
    if any(scope not in token.scopes for scope in scopes.scopes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return token


def get_current_user(
    token: OIDCToken = Depends(authenticate_user),
) -> User:
    return User(
        id=token.user_id,
        name=token.user_name,
        email=token.user_email,
        roles=token.roles,
    )


def JKPBasicAuth() -> Any:
    """
    Requires the user to be authenticated with the default openid scopes
    """
    return params.Security(
        authenticate_user_with_scope,
        scopes=[
            AuthScopes.OFFLINE_ACCESS,
            AuthScopes.OPENID,
            AuthScopes.PROFILE,
            AuthScopes.JKP_API,
            AuthScopes.EMAIL,
            AuthScopes.ROLES,
        ],
    )


class PermissionChecker:
    def __init__(self, require_permissions: list[AuthRole]) -> None:
        self.require_permissions = require_permissions

    def __call__(self, token: OIDCToken = JKPBasicAuth()) -> OIDCToken:
        if not token.is_in_any_role(self.require_permissions):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return token


def JKPRoleAuth(*, in_one_of: list[AuthRole]) -> Any:
    return params.Depends(PermissionChecker(in_one_of))


def JKPUserInfo() -> Any:
    return params.Depends(get_current_user)
