import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from asyncache import cached
from cachetools import TTLCache

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
lock = asyncio.Lock()


def hash_key(dt: datetime, tz: ZoneInfo) -> str:
    return f"{dt.replace(second=0, microsecond=0)}_{tz}"


@cached(cache=TTLCache(maxsize=128, ttl=2), key=hash_key)  # type: ignore[misc]
async def print_the_time_hash_key(dt: datetime, tz: ZoneInfo) -> None:
    await asyncio.sleep(0.01)
    logger.debug(f"It is {dt} in {tz}")


async def print_the_time(dt: datetime, tz: ZoneInfo) -> None:
    await asyncio.sleep(0.01)
    logger.debug(f"It is {dt} in {tz}")


async def call_hash_key(zone: str) -> None:
    """
    Without a lock, all calls go at the same time and are not caught by the cache.
    """
    async with lock:
        tz = ZoneInfo(zone)
        dt = datetime.now(tz=tz)
        await print_the_time_hash_key(dt, tz)


async def call_no_hash_key(zone: str) -> None:
    """
    With a lock, order is forced and the first call triggers the cache.
    Next calls use the cache.
    """
    async with lock:
        tz = ZoneInfo(zone)
        dt = datetime.now(tz=tz)
        await print_the_time(dt, tz)


async def main() -> None:
    for _ in range(3):
        for zone in ["Asia/Tokyo", "Europe/Paris", "America/Toronto"]:
            await asyncio.gather(*[call_no_hash_key(zone) for _ in range(3)])
        logger.debug("--")
        for zone in ["Africa/Bissau", "America/Fortaleza", "Asia/Tomsk"]:
            await asyncio.gather(*[call_hash_key(zone) for _ in range(3)])
        logger.debug("--")
        for zone in ["Pacific/Palau", "US/Alaska", "Australia/Lord_Howe"]:
            for _ in range(3):
                await asyncio.create_task(call_hash_key(zone))
        logger.debug("--")
        await asyncio.sleep(1)


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Running {__file__}")
    logger.info("=" * 80)
    asyncio.run(main())
