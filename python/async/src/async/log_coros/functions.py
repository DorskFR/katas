import asyncio


async def one():
    for i in range(3):
        await two()
    return 1


async def two():
    await asyncio.sleep(1)


async def three():
    for i in range(100):
        await asyncio.sleep(0.1)
