"""
Concurrent locks
"""

import asyncio
import logging
import time
from contextlib import suppress

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


async def canary() -> None:
    while True:
        await asyncio.sleep(0.1)
        logger.debug("-- canary --")


class Locked:
    def __init__(self, name: str, lock: asyncio.Lock | None = None) -> None:
        self._lock = lock or asyncio.Lock()
        self._name = name

    async def say_hello(self, sleep_time: float) -> None:
        start_time = time.monotonic()
        async with self._lock:
            await self.do_hello(sleep_time)
        logger.debug(f"{self._name}, elapsed {time.monotonic() - start_time} for a {sleep_time=}")

    async def do_hello(self, sleep_time: float) -> None:
        await asyncio.sleep(sleep_time)
        logger.debug(f"Hello I am {self._name}.")


async def multi_lock() -> None:
    locked1 = Locked("first")
    locked2 = Locked("second")
    locked3 = Locked("third")

    tasks = [
        locked1.say_hello(0.3),
        locked1.say_hello(0.2),
        locked1.say_hello(0.1),
        locked2.say_hello(0.3),
        locked2.say_hello(0.2),
        locked2.say_hello(0.1),
        locked3.say_hello(0.3),
        locked3.say_hello(0.2),
        locked3.say_hello(0.1),
    ]
    await asyncio.gather(*tasks)


async def shared_lock() -> None:
    lock = asyncio.Lock()
    locked1 = Locked("first", lock)
    locked2 = Locked("second", lock)
    locked3 = Locked("third", lock)
    tasks = [
        locked1.say_hello(0.3),
        locked1.say_hello(0.2),
        locked1.say_hello(0.1),
        locked2.say_hello(0.3),
        locked2.say_hello(0.2),
        locked2.say_hello(0.1),
        locked3.say_hello(0.3),
        locked3.say_hello(0.2),
        locked3.say_hello(0.1),
    ]
    await asyncio.gather(*tasks)


async def main() -> None:
    task = asyncio.create_task(canary())
    await multi_lock()
    logger.debug("---")
    await shared_lock()
    with suppress(asyncio.CancelledError):
        task.cancel()


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Running {__file__}")
    logger.info("=" * 80)
    asyncio.run(main())
