from barcode_api.deps.auth import JKPBasicAuth
from fastapi import APIRouter

from .routes import admin, image, lists, products, public, user

PUBLIC_ROUTES = [public, image]

AUTH_REQUIRED_ROUTES = [user, admin, products, lists]

public_router = APIRouter(tags=["public"])
authenticated_router = APIRouter(
    dependencies=[JKPBasicAuth()],
    tags=["authenticated"],
)

for entry in PUBLIC_ROUTES:
    public_router.include_router(entry.router)

for entry in AUTH_REQUIRED_ROUTES:
    authenticated_router.include_router(entry.router)


api_router = APIRouter()
api_router.include_router(public_router)
api_router.include_router(authenticated_router)
