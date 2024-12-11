import datetime
import uuid
from datetime import timedelta
from typing import Any

import jwt
from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from .._globals import ctx
from ..error_messages import ErrorMessages

settings = ctx.auth_settings


async def create_token(
    expires_delta: float, payload_data: dict[str, Any], secret_key: str
) -> tuple[str, dict]:
    iat = datetime.datetime.now(settings.timezone)
    exp = iat + timedelta(minutes=expires_delta)
    payload = {'exp': exp, 'iat': iat, 'jti': str(uuid.uuid4()), **payload_data}

    ready_jwt = jwt.encode(payload=payload, algorithm=settings.jwt.ALGORITHM, key=secret_key)
    return ready_jwt, payload


async def create_access_token(payload_data: dict[str, Any]) -> str:
    access_token = await create_token(
        settings.jwt.ACCESS_EXPIRE, payload_data, settings.jwt.ACCESS_KEY
    )
    return access_token[0]


async def create_refresh_token(payload_data: dict[str, Any]) -> tuple[str, dict]:
    return await create_token(
        settings.jwt.REFRESH_EXPIRE, payload_data, settings.jwt.REFRESH_KEY
    )


async def validate_payload(payload: dict[str, Any]) -> list[str]:
    exceptions = []

    expired_time = datetime.datetime.fromtimestamp(payload['exp'], settings.timezone)
    if expired_time < datetime.datetime.now(settings.timezone):
        exceptions.append(ErrorMessages.REFRESH_TOKEN_EXPIRED)

    return exceptions


async def get_credentials_from_token(token: str, key: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, algorithms=[settings.jwt.ALGORITHM], key=key)
    except jwt.exceptions.PyJWTError as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f'{ErrorMessages.INVALID_TOKEN_ACCESS}: {e}',
        ) from e

    payload_exceptions = await validate_payload(payload)
    if payload_exceptions:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=payload_exceptions)

    return payload
