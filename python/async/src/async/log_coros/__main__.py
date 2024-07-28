import asyncio
import time
import sys

from contextlib import suppress
from coros.log_coros.functions import one, three


def trace_calls(frame, event, arg):
    if event != "call":
        return
    co = frame.f_code
    filename = co.co_filename
    func_name = co.co_name
    module_name = frame.f_globals.get("__name__", "")

    if module_name == "__main__":
        print(f"Call to {func_name} on line {frame.f_lineno} of {filename}, module: {module_name}")

    return trace_calls


def enable_run():
    _run = asyncio.events.Handle._run

    def log_run(self):
        try:
            print(time.time(), self._callback.__self__._coro.cr_code.co_name)
        except AttributeError:
            print(time.time(), asyncio.base_events._format_handle(self))
        return _run(self)

    asyncio.events.Handle._run = log_run


async def main():
    handle = asyncio.create_task(three())
    for i in range(3):
        await one()
    await handle


if __name__ == "__main__":
    sys.settrace(trace_calls)

    # enable_run()
    # enable_is_coroutine()

    with suppress(KeyboardInterrupt):
        asyncio.run(main())
