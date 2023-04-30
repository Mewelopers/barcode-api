from barcode_api.deps.auth import JKPRoleAuth, JKPUserInfo
from barcode_api.schemas import AuthRole, User
from fastapi import APIRouter

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[JKPRoleAuth(in_one_of=[AuthRole.ADMIN])],
)


@router.get("/access", response_model=User)
def test_access(
    user: User = JKPUserInfo(),
) -> User:
    return user
