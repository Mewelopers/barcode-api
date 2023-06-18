import pytest

from fastapi import status
from httpx import AsyncClient


from barcode_api.schemas.token import OIDCToken


@pytest.mark.asyncio
async def test_get_user_token_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/user/token")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_user_token_authenticated(auth_client: AsyncClient, token: OIDCToken) -> None:
    response = await auth_client.get("/user/token")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["sub"] == token.sub


@pytest.mark.asyncio
async def test_get_user_info_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/user/me")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_get_user_info_authenticated(auth_client: AsyncClient, token: OIDCToken) -> None:
    resposne = await auth_client.get("/user/me")

    assert resposne.status_code == status.HTTP_200_OK
    assert resposne.json()["id"] == token.sub
    assert resposne.json()["email"] == token.email
    assert resposne.json()["name"] == token.name
    assert set(resposne.json()["roles"]) == token.roles
