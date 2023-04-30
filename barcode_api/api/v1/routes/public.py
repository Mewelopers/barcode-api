from fastapi import APIRouter

router = APIRouter()


@router.get("/hello")
def hello() -> str:
    return "Api is working correctly"
