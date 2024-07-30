from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

async_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
sessionmaker_ = async_sessionmaker(bind=async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def create_tables() -> None:
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def session_context() -> AsyncIterator[AsyncSession]:
    """session context manager"""

    # Since we are using an in-memory db
    await create_tables()

    async with sessionmaker_() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


DBSessionDep = Annotated[AsyncSession, Depends(session_context)]
