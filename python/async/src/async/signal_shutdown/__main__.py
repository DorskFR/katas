import asyncio

import os
import signal

signal.signal(signal.SIGTERM, lambda signum, frame: os.kill(os.getpid(), signal.SIGINT))


async def long_task():
    try:
        await asyncio.sleep(300)
    except asyncio.CancelledError:
        print("Long task shutting down")


async def kill_soon():
    await asyncio.sleep(1)
    os.kill(os.getpid(), signal.SIGTERM)


async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(long_task())
            tg.create_task(kill_soon())
    except asyncio.CancelledError:
        print("Main process shutting down")


if __name__ == "__main__":
    asyncio.run(main())
    print("Main process shutting down")
