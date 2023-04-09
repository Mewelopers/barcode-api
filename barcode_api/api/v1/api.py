from fastapi import APIRouter

from .routes import hello

api_router = APIRouter()
api_router.include_router(hello.router, tags=["hello"])
