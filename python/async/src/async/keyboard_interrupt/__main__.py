import asyncio


async def infinite() -> None:
    while True:
        print("Infinite loop, kill me with Ctrl + C")
        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(infinite())
    except KeyboardInterrupt:
        print("I caught a KeyboardInterrupt")
