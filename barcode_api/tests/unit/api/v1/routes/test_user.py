import pytest
from fastapi import status
from httpx import AsyncClient

from barcode_api.schemas.token import OIDCToken
from barcode_api.schemas.user import User


@pytest.mark.asyncio
async def test_get_user_token_signed(client: AsyncClient, mock_auth: OIDCToken) -> None:
    request = await client.get("user/token")

    assert request.status_code == status.HTTP_200_OK
    assert request.json()["sub"] == mock_auth.sub


@pytest.mark.asyncio
async def test_get_user_token_unauthorized(client: AsyncClient) -> None:
    request = await client.get("user/token")

    assert request.status_code == status.HTTP_403_FORBIDDEN
    assert request.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_user_info_unauthorized(client: AsyncClient) -> None:
    request = await client.get("user/me")

    assert request.status_code == status.HTTP_403_FORBIDDEN
    assert request.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_user_info_signed(client: AsyncClient, mock_user: User) -> None:
    request = await client.get("user/me")

    assert request.status_code == status.HTTP_200_OK
    assert request.json()["id"] == mock_user.id
    assert request.json()["email"] == mock_user.email
    assert request.json()["name"] == mock_user.name
    assert set(request.json()["roles"]) == mock_user.roles
