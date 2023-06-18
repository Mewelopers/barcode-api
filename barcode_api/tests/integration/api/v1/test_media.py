import asyncio
from uuid import UUID

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_image(
    client: AsyncClient,
    images_ids: list[UUID],
) -> None:
    async def test_for_id(id: UUID) -> None:
        response = await client.get(f"/image/{id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/jpeg"
        assert len(response.content) > 0

    tasks = [test_for_id(id) for id in images_ids]
    await asyncio.gather(*tasks)
