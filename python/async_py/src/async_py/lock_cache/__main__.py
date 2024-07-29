"""
Concurrent calls to an async function with a cache.
Without a lock, the calls all go through at the same time.
With a lock, the first call creates the cache and the next ones use it.
"""

import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from asyncache import cached
from cachetools import TTLCache

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
lock = asyncio.Lock()


@cached(cache=TTLCache(maxsize=1, ttl=10))  # type: ignore[misc]
async def print_the_time(zone: str) -> None:
    await asyncio.sleep(0.01)
    logger.debug(f"It is {datetime.now(tz=ZoneInfo(zone))} in {zone}")


async def print_the_time_no_lock(zone: str) -> None:
    """
    Without a lock, all calls go at the same time and are not caught by the cache.
    """
    await print_the_time(zone)


async def print_the_time_lock(zone: str) -> None:
    """
    With a call, order is forced and the first call triggers the cache.
    Next calls use the cache.
    """
    async with lock:
        await print_the_time(zone)


async def main() -> None:
    for zone in ["Asia/Tokyo", "Europe/Paris", "America/Toronto"]:
        await asyncio.gather(*[print_the_time_no_lock(zone) for _ in range(3)])
    logger.debug("--")
    for zone in ["Asia/Tokyo", "Europe/Paris", "America/Toronto"]:
        await asyncio.gather(*[print_the_time_lock(zone) for _ in range(3)])


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Running {__file__}")
    logger.info("=" * 80)
    asyncio.run(main())
