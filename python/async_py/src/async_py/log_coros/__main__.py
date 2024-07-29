import asyncio
import logging
import sys
import time
from contextlib import suppress


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


async def one() -> int:
    for _ in range(3):
        await two()
    return 1


async def two() -> None:
    await asyncio.sleep(1)


async def three() -> None:
    for _ in range(100):
        await asyncio.sleep(0.1)


def trace_calls(frame, event, arg):  # noqa: ARG001
    if event != "call":
        return None
    co = frame.f_code
    filename = co.co_filename
    func_name = co.co_name
    module_name = frame.f_globals.get("__name__", "")

    if module_name == "__main__":
        logger.debug(f"Call to {func_name} on line {frame.f_lineno} of {filename}, module: {module_name}")

    return trace_calls


def enable_run():
    _run = asyncio.events.Handle._run  # noqa: SLF001

    def log_run(self):
        try:
            logger.debug(time.time(), self._callback.__self__._coro.cr_code.co_name)  # noqa: SLF001
        except AttributeError:
            logger.debug(time.time(), asyncio.base_events._format_handle(self))  # noqa: SLF001
        return _run(self)

    asyncio.events.Handle._run = log_run  # noqa: SLF001


async def main():
    handle = asyncio.create_task(three())
    for _ in range(3):
        await one()
    await handle


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Running {__file__}")
    logger.info("=" * 80)
    sys.settrace(trace_calls)

    # enable_run()
    # enable_is_coroutine()

    with suppress(KeyboardInterrupt):
        asyncio.run(main())
