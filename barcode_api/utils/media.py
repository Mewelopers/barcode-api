from fastapi import Request

from barcode_api.models import Product


def add_media_urls(model: Product, request: Request) -> dict:
    """
    Returns the media urls for a product

    Args:
        model (Product): Product model instance
        request (Request): FastAPI request object

    Returns:
        dict: _description_
    """
    data = {}
    if model.barcode_image_uuid:
        data["barcode_image_url"] = request.url_for("get_image", image_uid=model.barcode_image_uuid).path
    if model.thumbnail_uuid:
        data["thumbnail_url"] = request.url_for("get_image", image_uid=model.thumbnail_uuid).path
    return data
