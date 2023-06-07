import logging
from typing import Any
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Request, Response

from barcode_api.deps.common import Service
from barcode_api.utils.media import add_media_urls
from barcode_api.schemas.products import ProductResponse, ProductBarcode, ProductInDb
from barcode_api.services.crud.product_crud import ProductCrud

router = APIRouter(prefix="/products", tags=["Products"])

logger = logging.getLogger(__name__)


@router.get("/{barcode}", response_model=ProductResponse)
async def get_product(
    barcode: str,
    request: Request,
    response: Response,
    productCrud: ProductCrud = Service(ProductCrud),
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
    local_result = await productCrud.get_by_barcode(product_search.barcode)
    if local_result:
        response.headers["X-Source"] = "local"
        return {
            **ProductInDb.from_orm(local_result).dict(),
            **add_media_urls(local_result, request),
        }

    result = await productCrud.find_online(product_search.barcode)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Product not found",
        )
    response.headers["X-Source"] = "online"

    return {
        **ProductResponse.from_orm(result).dict(),
        **add_media_urls(result, request),
    }
