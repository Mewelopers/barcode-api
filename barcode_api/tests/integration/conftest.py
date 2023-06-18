import random
import uuid
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from barcode_api.tests.types import MockImage
from barcode_api.tests.utils import random_image
from barcode_api.models.image_data import ImageData


@pytest.fixture(scope="function")
def list_of_images(request: pytest.FixtureRequest) -> list[MockImage]:
    sizes = [(100, 100), (200, 200), (300, 300), (400, 400), (500, 500)]
    marker = request.node.get_closest_marker("number_of_images")

    if marker is None:
        number_of_images = 10
    else:
        number_of_images = marker.args[0]

    def random_size() -> dict[str, int]:
        choice = random.choice(sizes)
        return {
            "width": choice[0],
            "height": choice[1],
        }

    return [random_image(**random_size()) for _ in range(number_of_images)]


@pytest_asyncio.fixture(scope="function")
async def images_ids(list_of_images: list[MockImage], session: AsyncSession) -> AsyncGenerator[list[uuid.UUID], None]:
    uuids = [uuid.uuid4() for _ in range(len(list_of_images))]
    images = [ImageData(id=id, data=data) for id, data in zip(uuids, map(lambda x: x.data, list_of_images))]

    for image in images:
        session.add(image)

    await session.commit()
    yield uuids

    delete_tasks = [session.delete(image) for image in images]
    await asyncio.gather(*delete_tasks)
