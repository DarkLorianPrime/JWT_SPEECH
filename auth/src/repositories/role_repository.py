from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.models import User, Role
from repositories.__meta__ import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)


async def get_role_repository(
        session: Annotated[AsyncSession, Depends(get_session)],
):
    return RoleRepository(session=session)
