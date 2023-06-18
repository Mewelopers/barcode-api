import pytest
from pytest_mock import MockFixture
from httpx import AsyncClient
from fastapi import status, FastAPI


from barcode_api.models.product import Product
from barcode_api.services.crud.product_crud import ProductCrud


@pytest.mark.asyncio
async def test_product_search_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/products/search", params={"query": "test"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.usefixtures("mock_auth")
@pytest.mark.asyncio
async def test_product_search(client: AsyncClient, products: list[Product], mocker: MockFixture, app: FastAPI) -> None:
    mock_crud = mocker.patch("barcode_api.api.v1.routes.products.ProductCrud", autospec=True)
    mock_crud.return_value.get_multi = mocker.AsyncMock(return_value=products)

    app.dependency_overrides[ProductCrud] = mock_crud

    response = await client.get("/products/search", params={"limit": "100"})
    assert response.status_code == status.HTTP_200_OK

    results = response.json()
    print(response.text)
    assert len(results) == len(products)

    for result in results:
        assert result["barcode"] in [product.barcode for product in products]
        assert result["name"] in [product.name for product in products]
        assert result["description"] in [product.description for product in products]


@pytest.mark.usefixtures("mock_auth")
@pytest.mark.asyncio
async def test_product_search_no_results(client: AsyncClient, mocker: MockFixture, app: FastAPI) -> None:
    mock_crud = mocker.patch("barcode_api.api.v1.routes.products.ProductCrud", autospec=True)
    mock_crud.return_value.get_multi = mocker.AsyncMock(return_value=[])

    app.dependency_overrides[ProductCrud] = mock_crud

    response = await client.get("/products/search", params={"limit": "100"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.usefixtures("mock_auth")
@pytest.mark.asyncio
async def test_get_product_search_query(client: AsyncClient, mocker: MockFixture, app: FastAPI) -> None:
    mock_crud = mocker.patch("barcode_api.api.v1.routes.products.ProductCrud", autospec=True)

    mock_crud.return_value.search = mocker.AsyncMock(return_value=[])

    app.dependency_overrides[ProductCrud] = mock_crud
    response = await client.get("/products/search", params={"query": "test"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
    assert mock_crud.return_value.search.call_count == 1
    assert mock_crud.return_value.search.call_args[0][0] == "test"
