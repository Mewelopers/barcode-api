import logging
import logging.config

from fastapi import FastAPI

from .api.v1.api import api_router
from .config import settings
from .middleware import ProcessTimeMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
    },
)
app.include_router(api_router, prefix=settings.API_V1_STR)
app.add_middleware(ProcessTimeMiddleware)

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)


def main() -> None:
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
