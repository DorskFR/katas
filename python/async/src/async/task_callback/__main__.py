import asyncio


async def divide_by_zero() -> None:
    await asyncio.sleep(3)
    raise ZeroDivisionError("division by zero")


async def main() -> None:
    task = asyncio.create_task(divide_by_zero())
    while True:
        print("Running...")
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
