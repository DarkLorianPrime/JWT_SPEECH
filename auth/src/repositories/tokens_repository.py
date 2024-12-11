from typing import Annotated

from database import get_session
from fastapi import Depends
from models.models import RefreshToken
from repositories.__meta__ import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class TokensRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)


async def get_tokens_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return TokensRepository(session=session)
