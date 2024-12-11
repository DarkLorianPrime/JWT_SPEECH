import settings
from jwt_auth import InitJWTAuth
from services.redis_service import get_tokens_controller

InitJWTAuth(tokens_controller=get_tokens_controller, jwt=settings.JWTSettings())

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated
from typing import Any
from uuid import UUID
from uuid import uuid4

from database import engine
from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from jwt_auth.auth import NonSecurityAccessController
from jwt_auth.auth import get_user_token
from models import Base
from services.user_car_service import UserCarService
from sqlalchemy import text


@asynccontextmanager
async def lifespan(_):
    async with engine.begin() as conn:
        is_car_exists = await conn.run_sync(engine.dialect.has_table, table_name='car')
        await conn.run_sync(Base.metadata.create_all)
        if not is_car_exists:
            car_insert_query = text("""
                INSERT INTO car (id, brand, model, manufactured_at, color, active) 
                VALUES (:id1, :brand1, :model1, :manufactured_at1, :color1, :active1), 
                       (:id2, :brand2, :model2, :manufactured_at2, :color2, :active2)
            """)
            await conn.execute(
                car_insert_query,
                {
                    'id1': str(uuid4()),
                    'brand1': 'BMW',
                    'model1': 'I8',
                    'manufactured_at1': datetime.strptime('09-01-2005', '%d-%m-%Y'),
                    'color1': 'white',
                    'active1': True,
                    'id2': str(uuid4()),
                    'brand2': 'Lada',
                    'model2': 'NeVesta',
                    'manufactured_at2': datetime.strptime('09-01-2024', '%d-%m-%Y'),
                    'color2': 'hell',
                    'active2': True,
                },
            )
    yield


app = FastAPI(
    lifespan=lifespan,
)
router = APIRouter(prefix='/api/v1/cars')


@router.get('/my-cars')
async def get_cars(
    user: Annotated[dict[str, Any], Depends(get_user_token)],
    user_car_service: Annotated[UserCarService, Depends()],
):
    return await user_car_service.get_cars_from_user(user['sub'])


@router.delete('/{user_id}/delete/{car_id}')
async def delete_car(
    user_id: UUID,
    car_id: UUID,
    user_car_service: Annotated[
        UserCarService,
        Depends(NonSecurityAccessController(True, 'admin').secure(UserCarService)),
    ],
):
    """
    Ставим hard_check True, потому что это опасное действие, и важно, чтобы роль была активна
    """
    return await user_car_service.delete_car(user_id, car_id)


@router.get('/{user_id}')
async def get_user_cars(
    user_id: UUID,
    user_car_service: Annotated[
        UserCarService,
        Depends(NonSecurityAccessController(False, 'admin').secure(UserCarService)),
    ],
):
    return await user_car_service.get_cars_from_user(user_id)


app.include_router(router)
