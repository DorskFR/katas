import logging
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fastapi_api.__main__ import app
from fastapi_api.database import Base, session_context

logger = logging.getLogger(__name__)


async_engine = create_async_engine("sqlite+aiosqlite:///:memory:")


@pytest.fixture(scope="session", autouse=True)
async def _create_tables() -> AsyncIterator[None]:
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    try:
        yield
    finally:
        async with async_engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture(name="client")
async def fixture_client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:  # type: ignore[arg-type]
        yield client


@pytest.fixture(autouse=True)
async def _session_override():
    async_session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False)

    async def get_session_override():
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[session_context] = get_session_override
