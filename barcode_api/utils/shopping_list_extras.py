from barcode_api.models import ShoppingListItem
from barcode_api.schemas import ShoppingListItemInDb

from fastapi import Request

from barcode_api.utils.media import add_media_urls


def add_extra(obj: ShoppingListItem, request: Request) -> dict:
    """
    Add the product barcode to a shopping list item response.

    Args:
        obj (ShoppingListItem): Instance of a shopping list item model

    Returns:
        dict: Response with product barcode
    """
    info = {
        **ShoppingListItemInDb.from_orm(obj).dict(),
    }

    if obj.product:
        info["product_barcode"] = obj.product.barcode
        info.update(**add_media_urls(model=obj.product, request=request))

    return info
