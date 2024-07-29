import asyncio
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


async def divide_by_zero() -> None:
    await asyncio.sleep(3)
    raise ZeroDivisionError("division by zero")


async def main() -> None:
    task = asyncio.create_task(divide_by_zero())
    while True:
        logger.debug("Running...")
        await asyncio.sleep(1)
    await task


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Running {__file__}")
    logger.info("=" * 80)
    asyncio.run(main())
