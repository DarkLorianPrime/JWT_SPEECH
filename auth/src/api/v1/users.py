from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from jwt_auth.error_messages import ErrorMessages
from jwt_auth.auth import get_user
from jwt_auth.auth.security.permission import AccessController
from models.models import User
from schemes.users import RefreshRequestSchema
from schemes.users import SignInRequestSchema
from schemes.users import SignInResponseSchema
from schemes.users import SignUpRequestSchema
from schemes.users import SignUpResponseSchema
from services.tokens_service import TokensService
from services.user_role_service import UserRolesService
from services.user_service import UserService
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_404_NOT_FOUND

users_router = APIRouter(prefix='/users')


@users_router.post('/signup', response_model=SignUpResponseSchema)
async def signup(
    credentials: Annotated[SignUpRequestSchema, Depends(SignUpRequestSchema.as_form)],
    account_service: Annotated[UserService, Depends()],
    user_roles_service: Annotated[UserRolesService, Depends()],
):
    if await account_service.is_user_exists(credentials):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail='This credentials already exists'
        )
    account = await account_service.create_user(credentials)
    await user_roles_service.set_user_role(account[0], 'user')

    await account_service.user_repository.commit()
    return account


@users_router.post('/signin', response_model=SignInResponseSchema)
async def signin(
    credentials: Annotated[SignInRequestSchema, Depends(SignInRequestSchema.as_form)],
    user_service: Annotated[UserService, Depends()],
    token_service: Annotated[TokensService, Depends()],
):
    account = await user_service.check_credentials_valid(credentials)
    if not account:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail='Login credentials are not valid'
        )
    tokens = await token_service.generate_tokens(account)
    await token_service.save_refresh_token(tokens['refresh_token_payload'], account.id)

    return tokens


@users_router.post('/refresh', response_model=SignInResponseSchema)
async def refresh_tokens(
    credentials: Annotated[RefreshRequestSchema, Depends(RefreshRequestSchema.as_form)],
    account_service: Annotated[UserService, Depends()],
    token_service: Annotated[TokensService, Depends()],
):
    token, jwt_payload = await token_service.get_refresh_payload(credentials.refresh_token)
    if isinstance(token, ErrorMessages):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=token)

    account = await account_service.get_by_refresh(jwt_payload)
    if isinstance(account, ErrorMessages):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=account)

    await token_service.disable_refresh(jwt_payload, disable_other=False)
    tokens = await token_service.generate_tokens(account)

    await token_service.save_refresh_token(tokens['refresh_token_payload'], account.id)

    return tokens


@users_router.delete('/{user_id}')
async def deactivate_account(
    user_id: UUID,
    tokens_service: Annotated[
        TokensService, Depends(AccessController('admin').secure(TokensService))
    ],
    user_service: Annotated[UserService, Depends()],
    user: Annotated[User, Depends(get_user)],
):
    if user.id != user_id and 'admin' not in user.roles:
        return None

    await tokens_service.kill_refresh_tokens(user_id)
    await tokens_service.kill_access_tokens(user_id)
    await user_service.deactivate_account(user_id)
