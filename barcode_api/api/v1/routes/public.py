from fastapi import APIRouter

router = APIRouter()


@router.get("/hello")
async def hello() -> str:
    return "Api is working correctly"
