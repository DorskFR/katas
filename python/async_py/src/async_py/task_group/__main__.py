"""
Asyncio TaskGroup replaces the concept of a nursery to create, delete tasks and catch exceptions
"""

import asyncio
import logging

from tenacity import RetryCallState, retry
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_attempt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class CustomError(Exception):
    """Custom error"""


async def sleep_talking(msg: str, number: int | None = None, *, is_true: bool = False) -> None:
    await asyncio.sleep(0.1)
    logger.debug(msg, number, is_true)


def after_print(state: RetryCallState) -> None:
    logger.debug(f"Failed {state.attempt_number} time(s)")


@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(CustomError),
    after=after_print,
    reraise=True,
)
async def raise_custom() -> None:
    await asyncio.sleep(0.1)
    raise CustomError("This is a custom error")


async def raise_another_error() -> None:
    raise ValueError("Not good!")


async def main() -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(sleep_talking("Hello", 10, is_true=True))
        tg.create_task(sleep_talking("World"))
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Running {__file__}")
    logger.info("=" * 80)
    asyncio.run(main())
