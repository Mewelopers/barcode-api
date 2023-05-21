import logging
from typing import Any

from barcode_api.deps.auth import JKPUserInfo
from barcode_api.deps.common import Service
from barcode_api.schemas import (
    ShoppingListCreate,
    ShoppingListCreateRequest,
    ShoppingListItemCreate,
    ShoppingListItemCreateRequest,
    ShoppingListItemResponse,
    ShoppingListResponse,
    ShoppingListUpdate,
    User,
)
from barcode_api.services.crud import ProductCrud, ShoppingListCrud, ShoppingListItemCrud
from barcode_api.services.scraping.exceptions import ParserException
from fastapi import APIRouter, HTTPException, status

router = APIRouter(tags=["shopping_list"])

logger = logging.getLogger(__name__)


@router.get("/lists", response_model=list[ShoppingListResponse])
async def get_shopping_lists(
    user: User = JKPUserInfo(), shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud)
) -> Any:
    return await shopping_list_crud.get_by_owner_user_id(user.id)


@router.post("/lists", response_model=ShoppingListResponse)
async def create_shopping_list(
    list_data: ShoppingListCreateRequest,
    user: User = JKPUserInfo(),
    shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud),
) -> Any:
    list_obj = await shopping_list_crud.create(obj_in=ShoppingListCreate(owner_user_id=user.id, **list_data.dict()))

    return list_obj


@router.get("/lists/{list_id}", response_model=ShoppingListResponse)
async def read_shopping_list(
    list_id: int, user: User = JKPUserInfo(), shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud)
) -> Any:
    list_obj = await shopping_list_crud.get(list_id)

    if list_obj is None or list_obj.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    return list_obj


@router.put("/lists/{list_id}", response_model=ShoppingListResponse)
async def update_shopping_list(
    list_id: int,
    list_data: ShoppingListCreateRequest,
    user: User = JKPUserInfo(),
    shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud),
) -> Any:
    list_obj = await shopping_list_crud.get(list_id)

    if list_obj is None or list_obj.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    updated = await shopping_list_crud.update(
        db_obj=list_obj, obj_in=ShoppingListUpdate(id=list_id, **list_data.dict(), owner_user_id=user.id)
    )

    return updated


@router.delete("/lists/{list_id}")
async def delete_shopping_list(
    list_id: int,
    user: User = JKPUserInfo(),
    shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud),
) -> Any:
    list_obj = await shopping_list_crud.get(list_id)

    if list_obj is None or list_obj.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    await shopping_list_crud.remove(id=list_id)

    return {
        "message": "Shopping list deleted",
    }


@router.get("/list-items/{list_id}")
async def get_shopping_list_items(
    list_id: int,
    user: User = JKPUserInfo(),
    shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud),
    shopping_list_item_crud: ShoppingListItemCrud = Service(ShoppingListItemCrud),
) -> list[ShoppingListItemResponse]:
    list_obj = await shopping_list_crud.get(list_id)

    if list_obj is None or list_obj.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    item_objs = await shopping_list_item_crud.get_by_list_id(list_id)

    return [
        ShoppingListItemResponse(
            id=item_obj.id,
            name=item_obj.name,
            list_id=item_obj.list_id,
            product_barcode=item_obj.product.barcode if item_obj.product else None,
        )
        for item_obj in item_objs
    ]


@router.post("/list-items/{list_id}")
async def create_shopping_list_item(
    list_id: int,
    item_data: ShoppingListItemCreateRequest,
    shopping_list_crud: ShoppingListCrud = Service(ShoppingListCrud),
    shopping_list_item_crud: ShoppingListItemCrud = Service(ShoppingListItemCrud),
    product_crud: ProductCrud = Service(ProductCrud),
) -> ShoppingListItemResponse:
    list_obj = await shopping_list_crud.get(list_id)

    if list_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found")

    if item_data.barcode is not None:
        print(item_data.barcode)
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

    return ShoppingListItemResponse(
        id=item_obj.id,
        name=item_obj.name,
        list_id=item_obj.list_id,
        product_barcode=item_obj.product.barcode if item_obj.product else None,
    )
