from typing import Annotated

from database import get_session
from fastapi import Depends
from models.models import Car
from repositories.__meta__ import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class CarRepository(BaseRepository[Car]):
    def __init__(self, session: AsyncSession):
        super().__init__(Car, session)


async def get_car_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return CarRepository(session=session)
