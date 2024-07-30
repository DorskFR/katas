from datetime import datetime

from pydantic import BaseModel, ConfigDict
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from fastapi_api.database import Base


class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    kingdom: Mapped[str] = mapped_column(nullable=False)
    clade: Mapped[str] = mapped_column(nullable=False)
    division: Mapped[str] = mapped_column(nullable=False)
    plant_class: Mapped[str] = mapped_column(nullable=False)
    is_edible: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )


class PlantBase(BaseModel):
    name: str
    kingdom: str
    clade: str
    division: str
    plant_class: str
    is_edible: bool


class PlantSchema(PlantBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class PlantCreate(PlantBase):
    pass


class PlantUpdate(BaseModel):
    id: int
    name: str | None = None
    kingdom: str | None = None
    clade: str | None = None
    division: str | None = None
    plant_class: str | None = None
    is_edible: bool | None = None
