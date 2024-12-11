import bcrypt
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from settings import settings


async def pydantic_exception_handler(_: Request, exc: ValidationError):
    new_errors = [
        {
            'type': error['type'],
            'loc': error['loc'],
            'message': error['msg'].lstrip('Value error,'),
            'input': error['input'],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({'detail': new_errors, 'Error': 'Fields is required'}),
    )


async def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        password=password.encode('utf-8'), salt=settings.SALT.encode('utf-8')
    ).decode('utf-8')