"""
Test for ordering guarantees in asyncio.

The consumer checks that for each task, the counter values are strictly increasing.
If any task's counter value decreases, an ordering violation is reported.

The goal is to test if the event loop will maintain the order when the system is under load.
This test should run in a docker container with limited resources.

As it turns out, even under load it seems the loop maintains the ordering.

This is likely due to using Future.add_done_callback()
https://docs.python.org/3.10/library/asyncio-future.html#asyncio.Future.add_done_callback

which call loop.call_soon() which maintains FIFO ordering.
https://docs.python.org/3.10/library/asyncio-eventloop.html#asyncio.loop.call_soon
"""

import asyncio
import logging
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

SLEEP_TIME = 1
done_event = asyncio.Event()


async def count(queue: asyncio.Queue[int]) -> None:
    i = 0
    while not done_event.is_set():
        await queue.put(i)
        i += 1
        await asyncio.sleep(SLEEP_TIME)


async def queue_consumer(queue: asyncio.Queue[int]) -> None:
    """
    Consumes from the queue and checks if values maintain their ordering.
    """
    last_i = 0
    iterations = 0

    while not done_event.is_set():
        i = await queue.get()
        if iterations % 10_000 == 0:
            logging.info(f"Processed {iterations} values. {i=}. Queue size: {queue.qsize()}")
        if i < last_i:
            logging.error(f"Order violation detected: {last_i} -> {i}")
            done_event.set()
        last_i = i
        iterations += 1


async def main() -> None:
    queue: asyncio.Queue[int] = asyncio.Queue()
    tasks: set[asyncio.Task[None]] = set()

    def done_callback(task: asyncio.Task[None]) -> None:
        tasks.discard(task)
        if len(tasks) == 0:
            done_event.set()

    for _ in range(100_000):
        task = asyncio.create_task(count(queue))
        task.add_done_callback(lambda t: done_callback(t))
        tasks.add(task)

    await queue_consumer(queue)

    while len(tasks) > 0:
        await done_event.wait()


if __name__ == "__main__":
    logging.info("=" * 80)
    logging.info(f"Running {__file__}")
    logging.info("=" * 80)
    start_time = time.time()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("Interrupted by user.")
    elapsed = time.time() - start_time
    logging.info(f"\nTotal test time: {elapsed:.2f} seconds")
