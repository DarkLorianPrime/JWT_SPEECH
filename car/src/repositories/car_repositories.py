from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.models import Car
from repositories.__meta__ import BaseRepository


class CarRepository(BaseRepository[Car]):
    def __init__(self, session: AsyncSession):
        super().__init__(Car, session)


async def get_car_repository(
        session: Annotated[AsyncSession, Depends(get_session)],
):
    return CarRepository(session=session)
