from fastapi import FastAPI

from .api.v1.api import api_router
from .config import settings

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
app.include_router(api_router, prefix=settings.API_V1_STR)


def main() -> None:
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
