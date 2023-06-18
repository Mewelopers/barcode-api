import pytest
from fastapi import FastAPI

from barcode_api.schemas.token import OIDCToken
from barcode_api.schemas.user import User
from ..utils import build_oidc_token


@pytest.fixture(scope="function")
def mock_auth(request: pytest.FixtureRequest, app: FastAPI) -> OIDCToken:
    from barcode_api.deps.auth import authenticate_user

    marker = request.node.get_closest_marker("roles")

    params = {}
    if marker is not None:
        params["roles"] = marker.args[0]

    marker = request.node.get_closest_marker("scopes")
    if marker is not None:
        params["scopes"] = marker.args[0]

    token = build_oidc_token(**params)

    app.dependency_overrides[authenticate_user] = lambda: token

    return token


@pytest.fixture(scope="function")
def mock_user(app: FastAPI, mock_auth: OIDCToken) -> User:
    from barcode_api.deps.auth import get_current_user

    user = User(
        id=mock_auth.sub,
        email=mock_auth.email,
        name=mock_auth.name,
        roles=mock_auth.roles,
    )

    app.dependency_overrides[get_current_user] = lambda: user

    return user
