import logging
from typing import Any
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Request, Response, Depends

from barcode_api.models.product import Product
from barcode_api.deps.common import Service
from barcode_api.utils.media import add_media_urls
from barcode_api.schemas.products import ProductResponse, ProductBarcode, ProductSearch
from barcode_api.services.crud.product_crud import ProductCrud

router = APIRouter(prefix="/products", tags=["Products"])

logger = logging.getLogger(__name__)


def construct_product_response(product: Product, request: Request) -> dict[str, Any]:
    return {
        **ProductResponse.from_orm(product).dict(),
        **add_media_urls(product, request),
    }


@router.get("/search", response_model=list[ProductResponse])
async def product_search(
    request: Request,
    params: ProductSearch = Depends(ProductSearch),
    product_crud: ProductCrud = Service(ProductCrud),
) -> Any:
    if params.query is None:
        result = await product_crud.get_multi(limit=params.limit)
        return [
            {
                **ProductResponse.from_orm(product).dict(),
                **add_media_urls(product, request),
            }
            for product in result
        ]

    result = await product_crud.search(params.query, limit=params.limit)

    return [construct_product_response(product=product, request=request) for product in result]


@router.get("/{barcode}", response_model=ProductResponse)
async def get_product(
    barcode: str,
    request: Request,
    response: Response,
    product_crud: ProductCrud = Service(ProductCrud),
) -> Any:
    """
    Get a product by its barcode. If the product is not found in the local database, it will be searched online.
    """
    try:
        product_search = ProductBarcode(barcode=barcode.strip())
    except ValueError as e:
        logging.info(f"Invalid barcode: {barcode}, error: %s", e)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid barcode",
        )

    # Try to find the product in the database
    local_result = await product_crud.get_by_barcode(product_search.barcode)
    if local_result:
        response.headers["X-Source"] = "local"
        return construct_product_response(local_result, request)

    result = await product_crud.find_online(product_search.barcode)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Product not found",
        )
    response.headers["X-Source"] = "online"

    return construct_product_response(result, request)
