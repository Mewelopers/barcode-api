from barcode_api.deps.auth import JKPBasicAuth
from fastapi import APIRouter

from .routes import admin, public, user

public_router = APIRouter(tags=["public"])
authenticated_router = APIRouter(
    dependencies=[JKPBasicAuth()],
    tags=["authenticated"],
)

# Include routers here
public_router.include_router(public.router)
authenticated_router.include_router(user.router)
authenticated_router.include_router(admin.router)


api_router = APIRouter()
api_router.include_router(public_router)
api_router.include_router(authenticated_router)
