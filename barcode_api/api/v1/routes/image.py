import uuid
from http import HTTPStatus

import magic
from barcode_api.deps.common import Service
from barcode_api.services.crud import ImageDataCrud
from fastapi import APIRouter, HTTPException, Response

router = APIRouter(prefix="/image", tags=["image"])


@router.get("/{image_uid}")
async def get_image(image_uid: uuid.UUID, image_crud: ImageDataCrud = Service(ImageDataCrud)) -> Response:
    image_data = await image_crud.get(id=image_uid)

    if image_data is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Image not found")

    image_bytes = image_data.data
    return Response(content=image_bytes, media_type=magic.from_buffer(image_bytes, mime=True))
