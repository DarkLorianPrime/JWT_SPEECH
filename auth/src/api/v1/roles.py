from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from jwt_auth.auth import get_user
from models.models import User
from starlette.status import HTTP_403_FORBIDDEN

role_router = APIRouter(prefix='/roles')


@role_router.get('/{user_id}')
async def get_user_role(
    account: Annotated[User, Depends(get_user)],
    user_id: UUID,
):
    user_role_names = {role.name for role in account.roles}
    if account.id == user_id or 'admin' in user_role_names:
        return account.roles

    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail='You do not have permission to get roles for this account',
    )
