from collections.abc import AsyncIterator

import pytest
import starlette
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from starlette_api.__main__ import build_app
from starlette_api.database.db_client import DatabaseClient
from starlette_api.database.models import Base


@pytest.fixture(name="db_client")
async def fixture_db_client() -> AsyncIterator[DatabaseClient]:
    # Create a test database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create a DatabaseClient instance
    db_client = DatabaseClient()
    await db_client.create_all()

    try:
        yield db_client
    finally:
        await db_client.drop_all()
        await db_client.shutdown()


@pytest.fixture(name="client")
async def client_fixture(db_client: DatabaseClient) -> AsyncIterator[AsyncClient]:
    app = build_app()
    app.state = starlette.datastructures.State({"db_client": db_client})
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
