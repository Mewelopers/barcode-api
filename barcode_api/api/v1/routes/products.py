import logging
from http import HTTPStatus

from barcode_api.deps.common import Service
from barcode_api.schemas.products import ProductResponse, ProductSearch
from barcode_api.services.crud.ProductCrud import ProductCrud
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/products", tags=["products"])
logger = logging.getLogger(__name__)


@router.get("/{barcode}")
async def get_product(
    barcode: str,
    productCrud: ProductCrud = Service(ProductCrud),
) -> ProductResponse:
    try:
        product_search = ProductSearch(barcode=barcode)
    except ValueError as e:
        logging.info(f"Invalid barcode: {barcode}, error: %s", e)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid barcode",
        )

    result = await productCrud.find_online(product_search.barcode)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Product not found",
        )

    return ProductResponse(
        id=result.id,
        barcode=result.barcode,
        name=result.name,
        description=result.description,
        manufacturer=result.manufacturer,
        thumbnail_url="test",
        barcode_image_url="test",
    )
