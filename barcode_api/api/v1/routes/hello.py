from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/hello")
async def hello() -> Any:
    return {"message": "Hello World"}
