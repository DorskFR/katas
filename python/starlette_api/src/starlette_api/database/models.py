from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON, Numeric


class Base(DeclarativeBase):
    pass


class Planet(Base):
    __tablename__ = "planets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    mass: Mapped[Decimal] = mapped_column(Numeric)
    volume: Mapped[Decimal] = mapped_column(Numeric)
    temperature: Mapped[Decimal] = mapped_column(Numeric)
    composition: Mapped[JSON] = mapped_column(JSON)
    aphelion: Mapped[Decimal] = mapped_column(Numeric)
    perihelion: Mapped[Decimal] = mapped_column(Numeric)
    orbital_speed: Mapped[Decimal] = mapped_column(Numeric)
    satellite_count: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "mass": self.mass,
            "volume": self.volume,
            "temperature": self.temperature,
            "composition": self.composition,
            "aphelion": self.aphelion,
            "perihelion": self.perihelion,
            "orbital_speed": self.orbital_speed,
            "satellite_count": self.satellite_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
