import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status, Request

from barcode_api.deps.auth import JKPUserInfo
from barcode_api.deps.common import Service
from barcode_api.schemas.user import User
from barcode_api.models.shopping_list_item import ShoppingListItem
from barcode_api.services.crud import ProductCrud, ShoppingListCrud, ShoppingListItemCrud
from barcode_api.services.scraping.exceptions import ParserException
from barcode_api.utils.media import add_media_urls
from barcode_api.schemas.shopping_list_item import (
    ShoppingListItemResponse,
    ShoppingListItemBody,
    ShoppingListItemCreate,
    ShoppingListItemInDb,
    ShoppingListItemUpdate,
)


router = APIRouter(tags=["Shopping List Items"])
logger = logging.getLogger(__name__)


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


@router.get("/list-items/{list_id}", response_model=list[ShoppingListItemResponse])
async def get_shopping_list_items(
    request: Request,
    list_id: int,
    user: User = JKPUserInfo(),
    shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud),
    shopping_list_item_crud: ShoppingListItemCrud = Service(ShoppingListItemCrud),
) -> Any:
    """
    Get all shopping list items for a shopping list

    Raises:
        HTTPException[HTTP_404_NOT_FOUND]: If the shopping list is not found
    """
    list_obj = await shopping_list_crud.get(id=list_id)

    if list_obj is None or list_obj.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    item_objs = await shopping_list_item_crud.get_items_by_list_id(list_id=list_id)

    return [add_extra(item, request) for item in item_objs]


@router.get("/list-items/{list_id}/{item_id}", response_model=ShoppingListItemResponse)
async def get_shopping_list_item(
    request: Request,
    list_id: int,
    item_id: int,
    user: User = JKPUserInfo(),
    shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud),
    shopping_list_item_crud: ShoppingListItemCrud = Service(ShoppingListItemCrud),
) -> Any:
    """
    Get all shopping list items for a shopping list

    Raises:
        HTTPException[HTTP_404_NOT_FOUND]: If the shopping list is not found
        HTTPException[HTTP_404_NOT_FOUND]: If the list item is not found
    """
    list_obj = await shopping_list_crud.get(id=list_id)

    if list_obj is None or list_obj.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    item = await shopping_list_item_crud.get_item_from_list(list_id=list_id, item_id=item_id)

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list item not found")

    return add_extra(item, request)


@router.post("/list-items/{list_id}", response_model=ShoppingListItemResponse)
async def create_shopping_list_item(
    request: Request,
    list_id: int,
    item_data: ShoppingListItemBody,
    shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud),
    shopping_list_item_crud: ShoppingListItemCrud = Service(ShoppingListItemCrud),
    product_crud: ProductCrud = Service(ProductCrud),
) -> Any:
    """
    Create a new shopping list item.

    Raises:
        HTTPException[HTTP_404_NOT_FOUND]: if the shopping list is not found
    """
    list_obj = await shopping_list_crud.get(list_id)

    if list_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    if item_data.barcode is not None:
        product = await product_crud.get_by_barcode(item_data.barcode)
        if product is None:
            try:
                product = await product_crud.find_online(item_data.barcode)
            except ParserException as e:
                logger.warning(f"Failed to find product online: {e}")
                product = None
    else:
        product = None

    item_obj = await shopping_list_item_crud.create(
        obj_in=ShoppingListItemCreate(**item_data.dict(), list_id=list_id, product_id=product.id if product else None)
    )

    return add_extra(item_obj, request)


@router.delete("/list-items/{list_id}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list_item(
    list_id: int,
    item_id: int,
    shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud),
    shopping_list_item_crud: ShoppingListItemCrud = Service(ShoppingListItemCrud),
) -> None:
    """
    Delete a shopping list item.

    Raises:
        HTTPException[HTTP_404_NOT_FOUND]: if the shopping list is not found
        HTTPException[HTTP_404_NOT_FOUND]: If the list item is not found
    """
    list_obj = await shopping_list_crud.get(list_id)

    if list_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    item = await shopping_list_item_crud.get_item_from_list(list_id=list_id, item_id=item_id)

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list item not found")

    await shopping_list_item_crud.remove(id=item_id)


@router.put("/list-items/{list_id}/{item_id}", response_model=ShoppingListItemResponse)
async def update_shopping_list_item(
    request: Request,
    list_id: int,
    item_id: int,
    body: ShoppingListItemBody,
    shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud),
    shopping_list_item_crud: ShoppingListItemCrud = Service(ShoppingListItemCrud),
    product_crud: ProductCrud = Service(ProductCrud),
) -> Any:
    """
    Update a shopping list item.
    Raises:
        HTTPException: _description_

    Returns:
        Any: _description_
    """
    list_obj = await shopping_list_crud.get(list_id)

    if list_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    item = await shopping_list_item_crud.get_item_from_list(list_id=list_id, item_id=item_id)

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list item not found")

    if body.barcode is not None:
        product = await product_crud.get_by_barcode(body.barcode)
        if product is None:
            try:
                product = await product_crud.find_online(body.barcode)
            except ParserException as e:
                logger.warning(f"Failed to find product online: {e}")
                product = None
        item.product = product

    obj = await shopping_list_item_crud.update(db_obj=item, obj_in=ShoppingListItemUpdate(**body.dict(), id=item_id))

    return add_extra(obj, request)
