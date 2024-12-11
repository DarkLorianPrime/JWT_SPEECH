from typing import Annotated
from typing import Any
from uuid import UUID

from fastapi import Depends
from jwt_auth.error_messages import ErrorMessages
from models.models import User
from repositories.user_repository import UserRepository
from repositories.user_repository import get_user_repository
from schemes.users import SignInRequestSchema
from schemes.users import SignUpRequestSchema
from utils import get_password_hash


class UserService:
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    ):
        self.user_repository = user_repository

    async def is_user_exists(self, credentials: SignUpRequestSchema):
        return await self.user_repository.is_exists(
            True,
            User.username == credentials.username,
            User.email == credentials.email,
        )

    async def create_user(self, params: SignUpRequestSchema):
        """Функция создания пользователя."""
        encrypted_password = await get_password_hash(params.password)

        params.password = encrypted_password
        new_user = await self.user_repository.create(params, User.id)

        return new_user

    async def check_credentials_valid(self, credentials: SignInRequestSchema):
        credentials.password = await get_password_hash(credentials.password)
        response = await self.user_repository.get_by_query(credentials)
        return response

    async def get_by_refresh(self, payload: dict[str, Any]) -> User | ErrorMessages:
        account = await self.user_repository.find(payload['sub'])
        if account is None:
            return ErrorMessages.INVALID_TOKEN_REFRESH

        return account

    async def deactivate_account(self, user_id: UUID):
        await self.user_repository.update([], User.id == user_id, active=False)
