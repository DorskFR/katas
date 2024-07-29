"""
Gather bypasses cache even with a lock as all coroutines are started at the same time
So gather should be used to schedule together coroutines which would return a different result
third and fourth iteration do not exhibit this behavior because we use create_task
"""

import asyncio
import logging

from asyncache import cached
from cachetools import TTLCache

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
lock = asyncio.Lock()


@cached(cache=TTLCache(maxsize=128, ttl=2))
async def count_gen(name: str) -> None:
    for i in range(3):
        await asyncio.sleep(0.01)
        logger.debug(f"[{name}] I am generating: {i}")


@cached(cache=TTLCache(maxsize=128, ttl=2))
async def count_loop(name: str) -> None:
    for i in [1, 2, 3]:
        await asyncio.sleep(0.01)
        logger.debug(f"[{name}] I am counting: {i}")


async def main() -> None:
    await asyncio.gather(*[count_gen("first") for _ in range(3)])
    await asyncio.sleep(1)

    async with lock:
        await asyncio.gather(*[count_loop("second") for _ in range(3)])
    await asyncio.sleep(1)

    for _ in range(3):
        await asyncio.create_task(count_gen("third"))
    await asyncio.sleep(1)

    for _ in range(3):
        await asyncio.create_task(count_loop("fourth"))
    await asyncio.sleep(1)

    tasks = [asyncio.create_task(count_loop("fifth")) for _ in range(3)]
    await asyncio.gather(*tasks)
    await asyncio.sleep(1)

    tasks2 = (asyncio.create_task(count_loop("sixth")) for _ in range(3))
    await asyncio.gather(*tasks2)
    await asyncio.sleep(1)


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Running {__file__}")
    logger.info("=" * 80)
    asyncio.run(main())
