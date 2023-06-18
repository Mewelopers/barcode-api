from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, URL


@pytest.fixture(scope="session")
def base_url() -> str:
    return "http://testserver/api/v1"


@pytest_asyncio.fixture(scope="function")
async def client(client: AsyncClient, base_url: str) -> AsyncGenerator[AsyncClient, None]:
    client.base_url = URL(base_url)
    yield client
