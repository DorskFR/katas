import asyncio
from contextlib import suppress

async def say_my_name(name: int) -> None:
    while True:
        print(f"My name is: {name}")
        await asyncio.sleep(0)


async def main() -> None:
    # Bypass the cache
    await asyncio.gather(*[say_my_name(i) for i in range(4)])


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
