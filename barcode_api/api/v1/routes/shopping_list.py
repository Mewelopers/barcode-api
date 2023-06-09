import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status, Request

from barcode_api.deps.auth import JKPUserInfo
from barcode_api.deps.common import Service
from barcode_api.schemas import ShoppingListItemResponse, ShoppingListItemBody, ShoppingListItemCreate
from barcode_api.schemas.shopping_list import (
    ShoppingListResponse,
    ShoppingListBody,
    ShoppingListCreate,
    ShoppingListUpdate,
)
from barcode_api.schemas.user import User
from barcode_api.services.crud import ShoppingListItemCrud, ProductCrud
from barcode_api.services.crud.shopping_list_crud import ShoppingListCrud
from barcode_api.services.scraping import ParserException
from barcode_api.utils.shopping_list_extras import add_extra

router = APIRouter(tags=["Shopping Lists"])
logger = logging.getLogger(__name__)


@router.get("/lists", response_model=list[ShoppingListResponse])
async def get_shopping_lists(
    user: User = JKPUserInfo(), shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud)
) -> Any:
    """
    Get all shopping lists for a user
    """
    return await shopping_list_crud.get_by_owner_user_id(user.id)


@router.get("/lists/{list_id}", response_model=ShoppingListResponse)
async def read_shopping_list(
    list_id: int, user: User = JKPUserInfo(), shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud)
) -> Any:
    """
    Get a shopping list by ID
    """
    list_obj = await shopping_list_crud.get(list_id)

    if list_obj is None or list_obj.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    return list_obj


@router.get("/lists/{list_id}/items", response_model=list[ShoppingListItemResponse])
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


@router.post("/lists", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
async def create_shopping_list(
    list_data: ShoppingListBody,
    user: User = JKPUserInfo(),
    shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud),
) -> Any:
    """
    Create a new shopping list
    """
    list_obj = await shopping_list_crud.create(obj_in=ShoppingListCreate(owner_user_id=user.id, **list_data.dict()))

    return list_obj


@router.post("/lists/{list_id}/items", response_model=ShoppingListItemResponse)
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


@router.put("/lists/{list_id}", response_model=ShoppingListResponse)
async def update_shopping_list(
    list_id: int,
    list_data: ShoppingListBody,
    user: User = JKPUserInfo(),
    shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud),
) -> Any:
    """
    Update an existing shopping list
    """
    list_obj = await shopping_list_crud.get(list_id)

    if list_obj is None or list_obj.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    updated = await shopping_list_crud.update(
        db_obj=list_obj, obj_in=ShoppingListUpdate(id=list_id, **list_data.dict(), owner_user_id=user.id)
    )

    return updated


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    list_id: int,
    user: User = JKPUserInfo(),
    shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud),
) -> None:
    """
    Delete a shopping list
    """
    list_obj = await shopping_list_crud.get(list_id)

    if list_obj is None or list_obj.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    await shopping_list_crud.remove(id=list_id)
