from abc import ABC
from typing import Annotated

from database import get_session
from fastapi import Depends
from models.models import User
from repositories.__meta__ import BaseRepository
from schemes.users import SignInRequestSchema
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AuthenticationMixin(BaseRepository, ABC):
    model: type[User]

    async def get_by_query(self, credentials: SignInRequestSchema):
        stmt = select(self.model).where(
            and_(
                or_(
                    self.model.email == credentials.login,
                    self.model.username == credentials.login,
                ),
                self.model.password == credentials.password,
                self.model.active.is_(True),
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar()


class UserRepository(AuthenticationMixin, BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return UserRepository(session=session)
