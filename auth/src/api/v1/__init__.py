from fastapi import APIRouter

from api.v1.logout import logout_router
from api.v1.roles import role_router
from api.v1.users import users_router

v1_router = APIRouter(prefix='/v1')
v1_router.include_router(users_router)
v1_router.include_router(logout_router)
v1_router.include_router(role_router)
