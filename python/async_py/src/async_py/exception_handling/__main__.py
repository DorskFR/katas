"""
Using try finally allows cleanup of asynchronous resources
"""

import asyncio
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Runnable:
    def __init__(self, name: str) -> None:
        self.is_running = True
        self.name = name

    def stop(self) -> None:
        self.is_running = False
        logger.debug(f"[{self.name}] has stopped")

    async def run(self) -> None:
        elapsed = 0
        while self.is_running:
            await asyncio.sleep(0)
            logger.debug(f"[{self.name}] is running...")

            if self.name == "1" and elapsed >= 3:
                raise RuntimeError("Too long!")
            elapsed += 1

    async def shutdown(self) -> None:
        self.stop()
        await asyncio.sleep(0)
        logger.debug(f"[{self.name}] has shut down")


async def main() -> None:
    runnables = [Runnable(name=str(i)) for i in range(5)]

    try:
        await asyncio.gather(*(runnable.run() for runnable in runnables))
    finally:
        await asyncio.gather(*(runnable.shutdown() for runnable in runnables))


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Running {__file__}")
    logger.info("=" * 80)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        logger.exception("Unhandled error")
