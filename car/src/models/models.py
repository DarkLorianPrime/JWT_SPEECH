import datetime

from sqlalchemy import UUID
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from models.__meta__ import Base


class Car(Base):
    __tablename__ = 'car'
    brand: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    manufactured_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    color: Mapped[str] = mapped_column(String)


class CarUser(Base):
    car_id: Mapped[Car] = mapped_column(UUID(as_uuid=True), ForeignKey('car.id'))
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
