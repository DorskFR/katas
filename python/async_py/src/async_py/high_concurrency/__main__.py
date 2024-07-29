"""
Multiple levels of concurrency can bypass cache

A lock is necessary for every level of concurrency
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
lock2 = asyncio.Lock()


def hash_key(dt: datetime, tz: ZoneInfo) -> str:
    return f"{dt}_{tz}"


@cached(cache=TTLCache(maxsize=3, ttl=1))
async def print_the_time(dt: datetime, tz: ZoneInfo) -> None:
    await asyncio.sleep(0.01)
    logger.debug(f"It is {dt} in {tz} {asyncio.current_task().get_name()}")


async def call_function(zone: str) -> None:
    """
    With a lock, order is forced and the first call triggers the cache.
    Next calls use the cache.
    """
    async with lock2:
        tz = ZoneInfo(zone)
        dt = datetime.now(tz=tz).replace(second=0, microsecond=0)
        await print_the_time(dt, tz)


async def super_call_function(zone: str) -> None:
    async with lock:
        await asyncio.gather(*[call_function(zone) for _ in range(3)])


async def main() -> None:
    # Bypass the cache
    await asyncio.gather(*[super_call_function("Asia/Tokyo") for _ in range(100)])


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Running {__file__}")
    logger.info("=" * 80)
    asyncio.run(main())
