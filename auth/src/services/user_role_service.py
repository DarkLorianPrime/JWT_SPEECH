from typing import Annotated

from fastapi import Depends
from models.models import Role
from repositories.role_repository import RoleRepository
from repositories.role_repository import get_role_repository
from repositories.user_repository import UserRepository
from repositories.user_repository import get_user_repository
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST


class UserRolesService:
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends(get_user_repository)],
        role_repository: Annotated[RoleRepository, Depends(get_role_repository)],
    ):
        self.role_repository = role_repository
        self.user_repository = user_repository

    async def set_user_role(self, user_id, role_name):
        """Функция присвоения роли пользователю."""
        user_role = await self.role_repository.get_by_query(Role.name == role_name)
        if user_role is None:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail='Роли нет в списке ролей'
            )
        user = await self.user_repository.find(user_id)
        if user_role not in user.roles:
            user.roles.append(user_role)
            await self.user_repository.commit()
        return user

    async def get_user_role(self, user_id):
        """Функция поиска пользователя."""
        user = await self.user_repository.find(user_id)
        return user
