import asyncio
import time

from asyncache import cached
from cachetools import TTLCache

lock = asyncio.Lock()


@cached(cache=TTLCache(maxsize=128, ttl=2))
async def count_gen(name: str) -> None:
    for i in range(3):
        await asyncio.sleep(0.01)
        print(f"[{name}] I am generating: {i}")


@cached(cache=TTLCache(maxsize=128, ttl=2))
async def count_loop(name: str) -> None:
    for i in [1, 2, 3]:
        await asyncio.sleep(0.01)
        print(f"[{name}] I am counting: {i}")


async def main() -> None:
    await asyncio.gather(*[count_gen("first") for _ in range(3)])
    time.sleep(1)

    async with lock:
        await asyncio.gather(*[count_loop("second") for _ in range(3)])
    time.sleep(1)

    for _ in range(3):
        await asyncio.create_task(count_gen("third"))
    time.sleep(1)

    for _ in range(3):
        await asyncio.create_task(count_loop("fourth"))
    time.sleep(1)

    tasks = [asyncio.create_task(count_loop("fifth")) for _ in range(3)]
    await asyncio.gather(*tasks)
    time.sleep(1)

    tasks2 = (asyncio.create_task(count_loop("sixth")) for _ in range(3))
    await asyncio.gather(*tasks2)
    time.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
