import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test(client: AsyncClient) -> None:
    response = await client.get("/ping")
    assert response.status_code == status.HTTP_200_OK
    assert response.text == '"Pong"'
