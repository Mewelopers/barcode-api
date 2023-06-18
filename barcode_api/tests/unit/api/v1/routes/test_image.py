from uuid import uuid4

import pytest
from fastapi import status, FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture

from barcode_api.services.crud import ImageDataCrud
from barcode_api.tests.types import MockImage


@pytest.mark.asyncio
async def test_get_image_404(client: AsyncClient, mocker: MockerFixture, app: FastAPI) -> None:
    mock_image_crud = mocker.stub(name="image_crud")

    type(mock_image_crud).get = mocker.AsyncMock(return_value=None)
    app.dependency_overrides[ImageDataCrud] = lambda: mock_image_crud

    uuid = uuid4()
    res = await client.get(f"/image/{uuid}")

    mock_image_crud.get.assert_called_once_with(id=uuid)
    assert res.status_code == status.HTTP_404_NOT_FOUND
    assert res.json() == {"detail": "Image not found"}


@pytest.mark.asyncio
async def test_get_image_random_image(
    client: AsyncClient, mocker: MockerFixture, image: MockImage, app: FastAPI
) -> None:
    mock_image_crud = mocker.stub(name="image_crud")

    mock_image_object = mocker.stub(name="image_object")
    data_property = mocker.PropertyMock(return_value=image.data)
    type(mock_image_object).data = data_property

    type(mock_image_crud).get = mocker.AsyncMock(return_value=mock_image_object)
    app.dependency_overrides[ImageDataCrud] = lambda: mock_image_crud

    uuid = uuid4()
    res = await client.get(f"/image/{uuid}")

    mock_image_crud.get.assert_called_once_with(id=uuid)
    data_property.assert_called_once()
    assert res.status_code == status.HTTP_200_OK
    assert res.content == image.data
    assert res.headers["Content-Type"] == image.content_type
