import asyncio
import functools
import logging
import signal
from collections.abc import AsyncGenerator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


# The custom signal handling loop factory
def _get_loop_with_signal_handling() -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()

    def cancel_all_tasks() -> None:
        for task in asyncio.all_tasks(loop):
            task.cancel()

    for sig in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(sig, cancel_all_tasks)

    return loop


# Custom asyncio runner that uses the signal handling loop
SignalRunner = functools.partial(asyncio.Runner, loop_factory=_get_loop_with_signal_handling)


async def infinite_loop() -> None:
    while True:
        await asyncio.sleep(1)


# An infinite asynchronous generator
async def infinite_async_gen() -> AsyncGenerator[int, None]:
    i = 0
    try:
        while i < 10:
            yield i
            i += 1
            await asyncio.sleep(0.1)
    finally:
        # This should be called during a graceful shutdown
        logger.debug("Async generator cleanup")


# Main coroutine that runs the generator
async def main():
    try:
        async for value in infinite_async_gen():
            logger.debug(value)
    except asyncio.CancelledError:
        logger.debug("Exiting")


# Example usage
if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Running {__file__}")
    logger.info("=" * 80)
    with SignalRunner() as runner:
        runner.run(main())
