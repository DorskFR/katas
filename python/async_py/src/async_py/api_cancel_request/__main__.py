"""
Check if an endpoint in a Starlette async API continues processing
when the client has cancelled the request.
"""

import asyncio
import logging

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


async def long_running_task():
    """Simulate a long-running task with 10 seconds of work"""
    logger.info("Starting long-running task")

    for i in range(10):
        logger.info(f"Working... step {i + 1}/10")
        await asyncio.sleep(1)

    logger.info("Long-running task completed")
    return "Task finished successfully"


async def test_endpoint(_: Request) -> JSONResponse:  # noqa: PT019
    logger.info("Endpoint called, starting long-running task")

    try:
        result = await long_running_task()
        logger.info("Returning response to client")
        return JSONResponse({"status": "success", "result": result})
    except asyncio.CancelledError:
        logger.info("Task was cancelled!")
        raise
    except Exception as e:
        logger.exception("Unexpected error")
        return JSONResponse({"status": "error", "message": str(e)})


routes = [
    Route("/test", test_endpoint, methods=["GET"]),
]

app = Starlette(routes=routes)

if __name__ == "__main__":
    logger.info("Starting server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
