import uuid

from sqlalchemy import UUID
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from models import Base

user_roles = Table(
    'account_roles',
    Base.metadata,
    Column('role_id', ForeignKey('role.id')),
    Column('user_id', ForeignKey('user.id')),
)


class User(Base):
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    roles: Mapped[list['Role']] = relationship(secondary=user_roles, lazy='selectin')


class Role(Base):
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)


class RefreshToken(Base):
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('user.id'), default=None, nullable=True
    )
    token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
    )
