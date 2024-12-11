import abc
import uuid
from typing import Any
from typing import Generic
from typing import TypeVar

from models import Base
from pydantic import BaseModel
from sqlalchemy import ColumnExpressionArgument
from sqlalchemy import Row
from sqlalchemy import exists
from sqlalchemy import insert
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

Model = TypeVar('Model', bound=Base)
BaseDataModel = TypeVar('BaseDataModel', bound=BaseModel)
CreateDataModel = TypeVar('CreateDataModel', bound=BaseModel)


class BaseRepository(abc.ABC, Generic[Model]):
    def __init__(self, model: type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    async def is_exists(self, use_or: bool = False, *args):
        args = args if not use_or else (or_(*args),)
        stmt = exists(self.model).where(*args).select()
        result = await self.session.execute(stmt)

        return result.scalar()

    async def create(
        self, credentials: CreateDataModel, *returning_fields: InstrumentedAttribute
    ) -> Row[Any] | None:
        stmt = (
            insert(self.model).values(**credentials.model_dump()).returning(*returning_fields)
        )
        result = await self.session.execute(stmt)

        if returning_fields:
            return result.first()

    async def find(self, row_id: str | uuid.UUID | int, model: bool = False) -> Model | None:
        stmt = (
            select(self.model)
            .where(self.model.id == row_id, self.model.active.is_(True))
            .limit(1)
        )

        result = await self.session.execute(stmt)
        if model:
            return result.scalars().first()

        return result.scalar()

    async def get_by_query(
        self,
        query: Any,
        order_by: list | None = None,
        first_row: bool = True,
        limit: int = None,
        offset: int = None,
    ):
        stmt = select(self.model).where(query)
        if order_by is not None:
            stmt = stmt.order_by(*order_by)

        if limit is not None:
            stmt = stmt.limit(limit)

        if offset is not None:
            stmt = stmt.offset(offset)

        result = await self.session.execute(stmt)
        result_scalar = result.scalars()
        if not first_row:
            return result_scalar.all()

        return result_scalar.first()

    async def update(
        self,
        returning_fields: list,
        *where: ColumnExpressionArgument[bool],
        **values: Any,
    ) -> Row[tuple[Any]] | None:
        stmt = update(self.model).where(*where).values(**values).returning(*returning_fields)
        result = await self.session.execute(stmt)
        await self.session.commit()
        if returning_fields:
            return result.first()

    async def commit(self):
        await self.session.commit()
