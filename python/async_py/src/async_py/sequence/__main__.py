"""
Shows that asyncio tasks keep their ordering when the event loop iterates on them.
Each break in the concurrency is known in advance and forms a sequence.
"""

import asyncio
import logging
from contextlib import suppress

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


async def say_my_name(name: int) -> None:
    while True:
        logger.debug(f"My name is: {name}")
        await asyncio.sleep(0)


async def start_gather() -> None:
    await asyncio.gather(*[say_my_name(i) for i in range(4)])


async def main() -> None:
    # Bypass the cache
    gather_task = asyncio.create_task(start_gather())
    await asyncio.sleep(1)
    with suppress(asyncio.CancelledError):
        gather_task.cancel()


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Running {__file__}")
    logger.info("=" * 80)
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
