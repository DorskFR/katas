from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from flask_api.database import db


class Animal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    order: Mapped[str] = mapped_column(nullable=False)
    family: Mapped[str] = mapped_column(nullable=False)
    genus: Mapped[str] = mapped_column(nullable=False)
    species: Mapped[str] = mapped_column(nullable=False)
    is_predator: Mapped[bool] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.current_timestamp())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "order": self.order,
            "family": self.family,
            "genus": self.genus,
            "species": self.species,
            "is_predator": self.is_predator,
            "updated_at": self.updated_at.timestamp(),
            "created_at": self.created_at.timestamp(),
        }
