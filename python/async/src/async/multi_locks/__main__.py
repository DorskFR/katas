import asyncio
import logging
import time
from collections.abc import Callable
from typing import Any

from cachetools import TTLCache, cached

logger = logging.getLogger(__name__)

async def canary() -> None:
    while True:
        await asyncio.sleep(.1)
        print("-- canary --")

class Locked:

    def __init__(self, name: str, lock: asyncio.Lock | None = None) -> None:
        self._lock = lock or asyncio.Lock()
        self._name = name

    async def say_hello(self, sleep_time: float) -> None:
        start_time = time.monotonic()
        async with self._lock:
            await self.do_hello(sleep_time)
        print(f"{self._name}, elapsed {time.monotonic() - start_time} for a {sleep_time=}")


    async def do_hello(self, sleep_time: float) -> None:
        await asyncio.sleep(sleep_time)
        print(f"Hello I am {self._name}.")


async def multi_lock() -> None:
    locked1 = Locked("first")
    locked2 = Locked("second")
    locked3 = Locked("third")

    tasks = [
        locked1.say_hello(.3),
        locked1.say_hello(.2),
        locked1.say_hello(.1),
        locked2.say_hello(.3),
        locked2.say_hello(.2),
        locked2.say_hello(.1),
        locked3.say_hello(.3),
        locked3.say_hello(.2),
        locked3.say_hello(.1),
    ]
    await asyncio.gather(*tasks)

async def shared_lock() -> None:

    lock = asyncio.Lock()
    locked1 = Locked("first", lock)
    locked2 = Locked("second", lock)
    locked3 = Locked("third", lock)
    tasks = [
        locked1.say_hello(.3),
        locked1.say_hello(.2),
        locked1.say_hello(.1),
        locked2.say_hello(.3),
        locked2.say_hello(.2),
        locked2.say_hello(.1),
        locked3.say_hello(.3),
        locked3.say_hello(.2),
        locked3.say_hello(.1),
    ]
    await asyncio.gather(*tasks)

async def main() -> None:
    asyncio.create_task(canary())
    await multi_lock()
    print("---")
    await shared_lock()


if __name__ == "__main__":
    asyncio.run(main())
