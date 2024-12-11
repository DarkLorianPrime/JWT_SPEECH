import datetime
from typing import Annotated
from typing import Any

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from ..._globals import ctx
from ...abstract import TokenControllerAbstract
from ...abstract import UserRepositoryAbstract
from ...exceptions import Exceptions
from ...utils.jwt_utils import get_credentials_from_token

settings = ctx.auth_settings


async def check_unavailable(jti_logout, jti_payload, disable_other, iat, disable_at):
    if jti_logout == jti_payload:
        return disable_other

    if disable_other:
        return iat > disable_at

    return True


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        description = """
        Project authentication, based on the JWT.
        """
        super().__init__(
            auto_error=auto_error, description=description, scheme_name='JWTBearer'
        )

    async def __call__(self, request: Request) -> dict[str, Any]:
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)
        if credentials is None:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=Exceptions.INVALID_TOKEN_ACCESS,
            )

        payload = await get_credentials_from_token(
            credentials.credentials, settings.jwt.ACCESS_KEY
        )

        now = datetime.datetime.now(datetime.UTC)
        expire_time = datetime.datetime.fromtimestamp(payload['exp'], datetime.UTC)
        if expire_time < now:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail='Access token is expired'
            )

        request.state.jwt_payload = payload
        return payload


security = JWTBearer()


class UserBearer:
    async def __call__(
        self,
        payload: Annotated[dict, Depends(security)],
        tokens_controller: Annotated[
            TokenControllerAbstract, Depends(settings.tokens_controller)
        ],
        user_repository: Annotated[UserRepositoryAbstract, Depends(settings.user_repository)],
    ):
        account_id: str | None = payload.get('sub')
        if account_id is None:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="'Sub' is not defined"
            )

        logout_token_info = await tokens_controller.get_from_cache(account_id)
        if logout_token_info and not await check_unavailable(
            jti_logout=logout_token_info['jti'],
            jti_payload=payload['jti'],
            iat=payload['iat'],
            disable_at=logout_token_info['disabled_at'],
            disable_other=logout_token_info['disable_other'],
        ):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail='Token is deactivated'
            )

        account = await user_repository.find(account_id)
        if not account:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail='Invalid authentication credentials',
            )

        return account


get_user = UserBearer()
