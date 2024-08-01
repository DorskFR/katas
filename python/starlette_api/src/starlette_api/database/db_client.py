import logging
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.sql import text

from starlette_api.database.models import Base

logger = logging.getLogger(__name__)


class DatabaseClient:
    def __init__(self) -> None:
        self._engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

    @asynccontextmanager
    async def connection_context(self) -> AsyncIterator[AsyncConnection]:
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    async def create_all(self) -> None:
        async with self.connection_context() as connection:
            await connection.run_sync(Base.metadata.create_all)
            logger.info("Created all tables")

    async def drop_all(self) -> None:
        async with self.connection_context() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            logger.info("Dropped all tables")

    async def execute(self, statement: str, bindings: dict[str, Any] | list[Any] | None = None) -> Sequence[Row[Any]]:
        async with self.connection_context() as connection:
            result = await connection.execute(text(statement), bindings)
            return result.fetchall()

    async def list_planets(self) -> list[dict[str, Any]]:
        stmt = "SELECT * FROM planets;"
        result = await self.execute(stmt)
        return [dict(row._mapping) for row in result]  # noqa: SLF001

    async def create_planet(self, bindings: dict[str, Any]) -> dict[str, Any]:
        stmt = """
        INSERT INTO planets (
            name,
            mass,
            volume,
            temperature,
            composition,
            aphelion,
            perihelion,
            orbital_speed,
            satellite_count,
            created_at,
            updated_at
        )
        VALUES (
            :name,
            :mass,
            :volume,
            :temperature,
            :composition,
            :aphelion,
            :perihelion,
            :orbital_speed,
            :satellite_count,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        RETURNING *;
        """
        result = await self.execute(stmt, bindings)
        row = result[0]
        return dict(row._mapping)  # noqa: SLF001

    async def get_planet(self, planet_id: int) -> dict[str, Any] | None:
        stmt = "SELECT * FROM planets WHERE id=:id;"
        result = await self.execute(stmt, {"id": planet_id})
        return dict(result[0]._mapping) if result else None  # noqa: SLF001

    async def update_planet(self, planet_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        set_clause = ", ".join(f"{k}=:{k}" for k in data)
        stmt = f"UPDATE planets SET {set_clause} WHERE id=:id RETURNING *;"
        result = await self.execute(stmt, {**data, "id": planet_id})
        return dict(result[0]._mapping) if result else None  # noqa: SLF001

    async def delete_planet(self, planet_id: int) -> bool:
        stmt = "DELETE FROM planets WHERE id=:id RETURNING id;"
        result = await self.execute(stmt, {"id": planet_id})
        return bool(result)

    async def session_context(self) -> AsyncIterator[AsyncSession]:
        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def shutdown(self):
        await self._engine.dispose()
