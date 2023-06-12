import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status, Request

from barcode_api.deps.auth import JKPUserInfo
from barcode_api.deps.common import Service
from barcode_api.schemas.user import User
from barcode_api.services.crud import ProductCrud, ShoppingListItemCrud
from barcode_api.services.scraping.exceptions import ParserException
from barcode_api.schemas.shopping_list_item import (
    ShoppingListItemResponse,
    ShoppingListItemBody,
    ShoppingListItemUpdate,
)
from barcode_api.utils.shopping_list_extras import add_extra

router = APIRouter(tags=["Shopping List Items"])
logger = logging.getLogger(__name__)


@router.get("/list-items/{item_id}", response_model=ShoppingListItemResponse)
async def get_shopping_list_item(
    request: Request,
    item_id: int,
    user: User = JKPUserInfo(),
    shopping_list_item_crud: ShoppingListItemCrud = Service(ShoppingListItemCrud),
) -> Any:
    """
    Get all shopping list items for a shopping list

    Raises:
        HTTPException[HTTP_404_NOT_FOUND]: If the shopping list is not found
        HTTPException[HTTP_404_NOT_FOUND]: If the list item is not found
    """
    # list_obj = await shopping_list_crud.get(id=list_id)
    #
    # if list_obj is None or list_obj.owner_user_id != user.id:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    item = await shopping_list_item_crud.get_item_from_list(item_id=item_id)

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list item not found")

    if item.list.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    return add_extra(item, request)


@router.delete("/list-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list_item(
    item_id: int,
    user: User = JKPUserInfo(),
    shopping_list_item_crud: ShoppingListItemCrud = Service(ShoppingListItemCrud),
) -> None:
    """
    Delete a shopping list item.

    Raises:
        HTTPException[HTTP_404_NOT_FOUND]: if the shopping list is not found
        HTTPException[HTTP_404_NOT_FOUND]: If the list item is not found
    """

    item = await shopping_list_item_crud.get_item_from_list(item_id=item_id)

    if item is None or item.list.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list item not found")

    await shopping_list_item_crud.remove(id=item_id)


@router.put("/list-items/{item_id}", response_model=ShoppingListItemResponse)
async def update_shopping_list_item(
    request: Request,
    item_id: int,
    body: ShoppingListItemBody,
    user: User = JKPUserInfo(),
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
    item = await shopping_list_item_crud.get_item_from_list(item_id=item_id)

    if item is None or item.list.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list item not found")

    if body.barcode is not None and body.barcode != getattr(item.product, "barcode", None):
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
