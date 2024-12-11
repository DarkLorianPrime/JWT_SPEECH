from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from jwt_auth.auth import get_user
from models.models import User
from schemes.users import RefreshRequestSchema
from services.tokens_service import TokensService
from starlette.requests import Request

logout_router = APIRouter(prefix='/logout')


@logout_router.post(
    '/',
    summary='Выход из аккаунта',
    description="""Добавление refresh-токена в список инактивных.
    Добавление disable_all=False только для этого access токена""",
    response_model=None,
)
async def logout_session(
    request: Request,
    credentials: Annotated[RefreshRequestSchema, Depends(RefreshRequestSchema.as_form)],
    account: Annotated[User, Depends(get_user)],
    token_service: Annotated[TokensService, Depends()],
):
    await token_service.disable_tokens(account, credentials, request.state.jwt_payload)


@logout_router.post(
    '/all',
    summary='Выход из аккаунта для всех других сессий',
    description="""Добавление всех refresh-tokenов в неактивные.
    Добавление disable_all в redis для всех access токенов.""",
    response_model=None,
)
async def logout_other_sessions(
    request: Request,
    credentials: Annotated[RefreshRequestSchema, Depends(RefreshRequestSchema.as_form)],
    account: Annotated[User, Depends(get_user)],
    service: Annotated[TokensService, Depends()],
):
    await service.disable_tokens(account, credentials, request.state.jwt_payload, True)
