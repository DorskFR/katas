import asyncio
import signal
import functools
from typing import AsyncGenerator


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
SignalRunner = functools.partial(
    asyncio.Runner, loop_factory=_get_loop_with_signal_handling
)

async def infinite_loop() -> None:
    while True:
        await asyncio.sleep(10)

# An infinite asynchronous generator
async def infinite_async_gen() -> AsyncGenerator[int, None]:
    i = 0
    try:
        while True:
            yield i
            i += 1
            await asyncio.sleep(1)
    finally:
        # This should be called during a graceful shutdown
        print("Async generator cleanup")


# Main coroutine that runs the generator
async def main():
    try:
        async for value in infinite_async_gen():
            print(value)
    except asyncio.CancelledError:
        print("Exiting")

# Example usage
if __name__ == "__main__":
    with SignalRunner() as runner:
        runner.run(main())
