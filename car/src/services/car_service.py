from typing import Annotated

from fastapi.params import Depends
from repositories.car_repositories import CarRepository
from repositories.car_repositories import get_car_repository


class CarService:
    def __init__(self, car_repository: Annotated[CarRepository, Depends(get_car_repository)]):
        self.car_repository = car_repository
