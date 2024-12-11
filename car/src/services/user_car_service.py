from typing import Annotated
from uuid import UUID

from fastapi.params import Depends
from sqlalchemy import and_

from models import Car, CarUser
from repositories.user_car_repositories import (
    UserCarRepository,
    get_user_car_repository,
)


class UserCarService:
    def __init__(
        self,
        user_car_repository: Annotated[
            UserCarRepository, Depends(get_user_car_repository)
        ],
    ):
        self.user_car_repository = user_car_repository


    async def get_cars_from_user(self, user_id: UUID):
        return await self.user_car_repository.get_by_query(
            and_(
                CarUser.user_id == user_id,
                CarUser.active.is_(True)
            ),
            joins=[[CarUser, CarUser.car_id == Car.id]],
            custom_return=[Car],
            first_row=False
        )

    async def delete_car(self, user_id: UUID, car_id: UUID):
        await self.user_car_repository.update(
            [], CarUser.car_id == car_id, CarUser.user_id == user_id, active=False
        )