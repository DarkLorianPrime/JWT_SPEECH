from abc import ABC
from abc import abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy.orm import DeclarativeBase


class TokenControllerAbstract(ABC):
    @abstractmethod
    async def get_from_cache(self, detail_uuid: UUID | str) -> dict[str, Any] | Any | None:
        raise NotImplementedError


class UserRepositoryAbstract(ABC):
    @abstractmethod
    async def find(self, row_id: str | UUID | int) -> DeclarativeBase:
        raise NotImplementedError
