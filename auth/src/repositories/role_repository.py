from typing import Annotated

from database import get_session
from fastapi import Depends
from models.models import Role
from repositories.__meta__ import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)


async def get_role_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return RoleRepository(session=session)
