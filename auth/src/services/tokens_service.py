import datetime
from collections.abc import Iterable
from typing import Annotated
from typing import Any
from uuid import UUID

from fastapi import Depends
from jwt_auth._globals import ctx
from jwt_auth.error_messages import ErrorMessages
from jwt_auth.utils import create_access_token
from jwt_auth.utils import create_refresh_token
from jwt_auth.utils import get_credentials_from_token
from models.models import RefreshToken
from models.models import Role
from models.models import User
from repositories.tokens_repository import TokensRepository
from repositories.tokens_repository import get_tokens_repository
from schemes.users import RefreshRequestSchema
from schemes.users import RefreshTokenSchema
from services.redis_service import TokensRedisController
from services.redis_service import get_tokens_controller
from sqlalchemy import Row


class TokensService:
    def __init__(
        self,
        token_controller: Annotated[TokensRedisController, Depends(get_tokens_controller)],
        token_repository: Annotated[TokensRepository, Depends(get_tokens_repository)],
    ):
        self.tokens_controller = token_controller
        self.token_repository = token_repository

    async def parse_payload_model(self, models: Iterable[Role]) -> list[str]:
        new_data = []
        for model in models:
            new_data.append(str(model.name))

        return new_data

    async def generate_tokens(self, account: User) -> dict[str, str | dict]:
        payload = {
            'sub': str(account.id),
        }
        refresh_token = await create_refresh_token(payload)
        return {
            'access_token': await create_access_token(
                {
                    **payload,
                    'roles': await self.parse_payload_model(account.roles),
                }
            ),
            'refresh_token': refresh_token[0],
            'refresh_token_payload': refresh_token[1],
        }

    async def disable_refresh(self, payload: dict[str, Any], disable_other: bool) -> None:
        where = [
            RefreshToken.user_id == payload['sub'],
            (
                RefreshToken.token_id != payload['jti']
                if disable_other
                else RefreshToken.token_id == payload['jti']
            ),
        ]

        await self.token_repository.update([], *where, active=False)

    async def disable_tokens(
        self,
        user: User,
        credentials: RefreshRequestSchema,
        payload: dict[str, Any],
        disable_other: bool = False,
    ) -> None:
        now_time = datetime.datetime.now(ctx.settings.timezone).timestamp()
        cache_object = {
            'id': str(user.id),
            'disable_other': disable_other,
            'jti': payload['jti'],
            'disabled_at': now_time,
        }
        ttl = payload['exp'] - now_time
        await self.tokens_controller.put_to_cache(cache_object, ttl)

        refresh_payload: dict[str, Any] = await get_credentials_from_token(
            credentials.refresh_token, ctx.auth_settings.jwt.REFRESH_KEY
        )
        await self.disable_refresh(refresh_payload, disable_other)

    async def save_refresh_token(self, refresh_payload: dict[str, Any], user_id: str | UUID):
        token_history = RefreshTokenSchema(token_id=refresh_payload['jti'], user_id=user_id)
        await self.token_repository.create(token_history)
        await self.token_repository.commit()

    async def get_by_jwt_id(self, jti: str | UUID) -> ErrorMessages | Row:
        token_record = await self.token_repository.get_by_query(RefreshToken.token_id == jti)
        if token_record is None or not token_record.active:
            return ErrorMessages.TOKEN_NOT_AVAILABLE

        return token_record

    async def get_refresh_payload(self, refresh_token: str) -> tuple[str | Row, dict[str, Any]]:
        payload: dict[str, Any] = await get_credentials_from_token(
            refresh_token, ctx.settings.jwt.REFRESH_KEY
        )
        token_record = await self.get_by_jwt_id(payload['jti'])

        return token_record, payload

    async def kill_refresh_tokens(self, user_id: UUID):
        await self.token_repository.update([], RefreshToken.user_id == user_id, active=False)

    async def kill_access_tokens(self, user_id: UUID):
        now_time = datetime.datetime.now(ctx.auth_settings.timezone).timestamp()
        cache_object = {
            'id': str(user_id),
            'disable_other': True,
            'jti': 'FORCE DISABLE',
            'disabled_at': now_time,
        }
        ttl = ctx.auth_settings.jwt.ACCESS_EXPIRE * 60
        await self.tokens_controller.put_to_cache(cache_object, ttl)
