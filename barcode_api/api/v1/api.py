from fastapi import APIRouter

from .routes import auth, hello, user

api_router = APIRouter()
api_router.include_router(hello.router, tags=["hello"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
