from barcode_api.deps.auth import JKPBasicAuth
from fastapi import APIRouter

from .routes import admin, products, public, user

PUBLIC_ROUTES = [public]

AUTH_REQUIRED_ROUTES = [user, admin, products]

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
