from uuid import uuid4

from sqlalchemy import UUID, Boolean
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, default=uuid4, primary_key=True
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)