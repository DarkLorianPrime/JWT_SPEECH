import datetime

from sqlalchemy import String, DateTime, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.__meta__ import Base


class Car(Base):
    __tablename__ = "car"
    brand: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    manufactured_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    color: Mapped[str] = mapped_column(String)


class CarUser(Base):
    car_id: Mapped[Car] = mapped_column(UUID(as_uuid=True), ForeignKey("car.id"))
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
