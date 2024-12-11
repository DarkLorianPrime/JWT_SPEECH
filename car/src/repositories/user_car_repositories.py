from typing import Annotated

from database import get_session
from fastapi import Depends
from models.models import CarUser
from repositories.__meta__ import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class UserCarRepository(BaseRepository[CarUser]):
    def __init__(self, session: AsyncSession):
        super().__init__(CarUser, session)


async def get_user_car_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return UserCarRepository(session=session)
