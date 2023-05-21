import logging
from http import HTTPStatus

from barcode_api.deps.common import Service
from barcode_api.models import Product
from barcode_api.schemas.products import ProductCommon, ProductMediaIds, ProductResponse, ProductSearch
from barcode_api.services.crud.product_crud import ProductCrud
from fastapi import APIRouter, HTTPException, Request, Response

router = APIRouter(prefix="/products", tags=["products"])

logger = logging.getLogger(__name__)


@router.get("/{barcode}")
async def get_product(
    barcode: str,
    request: Request,
    response: Response,
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

    def get_media_urls(model: Product) -> dict:
        return {
            "barcode_image_url": None
            if model.barcode_image_uuid is None
            else request.url_for("get_image", image_uid=model.barcode_image_uuid).path,
            "thumbnail_url": None
            if model.thumbnail_uuid is None
            else request.url_for("get_image", image_uid=model.thumbnail_uuid).path,
        }

    # Try to find the product in the database
    local_result = await productCrud.get_by_barcode(product_search.barcode)
    if local_result:
        response.headers["X-Source"] = "local"
        return ProductResponse(
            id=local_result.id,
            **ProductCommon.from_orm(local_result).dict(),
            **ProductMediaIds.from_orm(local_result).dict(),
            **get_media_urls(local_result),
        )

    result = await productCrud.find_online(product_search.barcode)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Product not found",
        )
    response.headers["X-Source"] = "online"

    return ProductResponse(
        id=result.id,
        **ProductCommon.from_orm(result).dict(),
        **ProductMediaIds.from_orm(result).dict(),
        **get_media_urls(result),
    )
