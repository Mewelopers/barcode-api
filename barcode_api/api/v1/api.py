from barcode_api.deps.auth import JKPBasicAuth
from fastapi import APIRouter

from .routes import image, products, public, user, shopping_list, shopping_list_item

PUBLIC_ROUTES = [public, image]
AUTH_REQUIRED_ROUTES = [user, products, shopping_list, shopping_list_item]

public_router = APIRouter()
authenticated_router = APIRouter(
    dependencies=[JKPBasicAuth()],
)

for entry in PUBLIC_ROUTES:
    public_router.include_router(entry.router)

for entry in AUTH_REQUIRED_ROUTES:
    authenticated_router.include_router(entry.router)

api_router = APIRouter()
api_router.include_router(public_router)
api_router.include_router(authenticated_router)
