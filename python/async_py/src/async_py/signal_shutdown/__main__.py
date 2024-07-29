import asyncio
import logging
import os
import signal

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
signal.signal(signal.SIGTERM, lambda signum, frame: os.kill(os.getpid(), signal.SIGINT))  # noqa: ARG005


async def long_task():
    try:
        await asyncio.sleep(300)
    except asyncio.CancelledError:
        logger.debug("Long task shutting down")


async def kill_soon():
    await asyncio.sleep(1)
    os.kill(os.getpid(), signal.SIGTERM)


async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(long_task())
            tg.create_task(kill_soon())
    except asyncio.CancelledError:
        logger.debug("Main process shutting down")


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Running {__file__}")
    logger.info("=" * 80)
    asyncio.run(main())
    logger.debug("Main process shutting down")
