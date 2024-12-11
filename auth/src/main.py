from uuid import uuid4

from jwt_auth import InitJWTAuth
from sqlalchemy import text

from utils import get_password_hash
from repositories.user_repository import get_user_repository
from settings import JWTSettings
from services.redis_service import get_tokens_controller

InitJWTAuth(
    tokens_controller=get_tokens_controller,
    user_repository=get_user_repository,
    jwt=JWTSettings(),
)

from api import api_router
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import ValidationError

from database import engine
from models import Base
from utils import pydantic_exception_handler


@asynccontextmanager
async def lifespan(_):
    async with engine.begin() as conn:
        is_role_exists = await conn.run_sync(
            engine.dialect.has_table, table_name="role"
        )
        await conn.run_sync(Base.metadata.create_all)
        if not is_role_exists:
            role_insert_query = text("""
                INSERT INTO role (id, name, active) 
                VALUES (:id1, :name1, :active1), 
                       (:id2, :name2, :active2)
            """)
            admin_id = str(uuid4())
            await conn.execute(
                role_insert_query,
                {
                    "id1": str(uuid4()),
                    "name1": "user",
                    "active1": True,
                    "id2": admin_id,
                    "name2": "admin",
                    "active2": True,
                },
            )

            create_user_query = text("""
                INSERT INTO "user" (id, email, username, password, active)
                VALUES (:id, :email, :username, :password, :active)
            """)
            user_id = str(uuid4())
            await conn.execute(
                create_user_query,
                {
                    "id": user_id,
                    "email": "admin@test.email",
                    "username": "debug_user",
                    "password": await get_password_hash("password"),
                    "active": True,
                },
            )
            await conn.execute(
                create_user_query,
                {
                    "id": str(uuid4()),
                    "email": "user@test.email",
                    "username": "debug_user_2",
                    "password": await get_password_hash("password"),
                    "active": True,
                },
            )

            set_admin_query = text("""
            INSERT INTO account_roles (user_id, role_id)
            VALUES (:user_id, :role_id)
            """)
            await conn.execute(
                set_admin_query,
                {
                    "user_id": user_id,
                    "role_id": admin_id,
                },
            )

    yield


app = FastAPI(
    lifespan=lifespan,
)

app.add_exception_handler(
    ValidationError,
    pydantic_exception_handler,
)  # type: ignore

app.include_router(api_router)
