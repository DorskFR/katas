import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Mount, Route
from starlette.types import Lifespan

from starlette_api.database.db_client import DatabaseClient
from starlette_api.mounts.planets import planets_routes
from starlette_api.state import State

logging.basicConfig(level=logging.INFO)


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = datetime.now(tz=UTC)
        response = await call_next(request)
        process_time = datetime.now(tz=UTC) - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


@asynccontextmanager
async def default_lifespan(_app: Starlette) -> AsyncIterator[State]:
    db_client = DatabaseClient()
    await db_client.create_all()
    try:
        yield {"db_client": db_client}
    finally:
        await db_client.shutdown()


async def shutdown_event() -> None:
    await app.state.db_client.drop_all()


async def root(_request: Request):
    return JSONResponse({"hello": "world"})


async def health(_request: Request) -> PlainTextResponse:
    return PlainTextResponse(content="OK")


def build_app(lifespan: Lifespan[Starlette] = default_lifespan) -> Starlette:
    return Starlette(
        debug=True,
        routes=[
            Mount("/planets", routes=planets_routes),
            Route("/", root),
        ],
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=False,
                allow_methods=["GET", "POST"],
                allow_headers=["*"],
            ),
            Middleware(ProcessTimeMiddleware),
        ],
        lifespan=lifespan,
    )


if __name__ == "__main__":
    app = build_app()
    uvicorn.run(app, host="0.0.0.0", port=8080)
