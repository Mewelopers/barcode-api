from fastapi import APIRouter

router = APIRouter()


@router.get("/ping", tags=["Public"])
async def ping() -> str:
    """
    Test endpoint to check if the API is working
    """
    return "Pong"
