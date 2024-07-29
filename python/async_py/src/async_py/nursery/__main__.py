"""
A task nursery, the ancestor of asyncio.TaskGroup used to create, delete tasks and catch exceptions
"""

import asyncio
import logging
from asyncio import CancelledError, Task
from collections.abc import Coroutine
from typing import Any

from tenacity import RetryCallState, retry
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_attempt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class CustomError(Exception):
    """Custom error"""


async def sleep_talking(msg: str, number: int | None = None, *, is_true: bool = False) -> None:
    await asyncio.sleep(0.1)
    logger.debug(msg, number, is_true)


def after_print(state: RetryCallState) -> None:
    logger.debug(f"Failed {state.attempt_number} time(s)")


@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(CustomError),
    after=after_print,
    reraise=True,
)
async def raise_custom() -> None:
    await asyncio.sleep(0.1)
    raise CustomError("This is a custom error")


async def raise_another_error() -> None:
    raise ValueError("Not good!")


class Nursery:
    def __init__(self, silenced_errors: Exception | tuple[Any, ...] | None = None) -> None:
        super().__init__()
        self.tasks: set[Task[None]] = set()
        self.silenced_errors: Exception | tuple[Any, ...] = silenced_errors or ()

    def create_task(self, coroutine: Coroutine[Any, Any, None]) -> None:
        task = asyncio.create_task(coroutine)
        task.add_done_callback(self.done_callback)
        self.tasks.add(task)

    def done_callback(self, task: Task[None]) -> None:
        try:
            task.result()
        except CancelledError:
            logger.debug("Silencing a CancelledError.")
        except self.silenced_errors:
            logger.debug("Silencing a CustomError.")
        except Exception:
            logger.debug("Raising this one:")
            raise
        finally:
            self.tasks.discard(task)

    def cleanup_tasks(self) -> None:
        for task in self.tasks:
            task.cancel()


async def main() -> None:
    nursery = Nursery(CustomError)  # or Nursery((CustomError, ValueError))
    nursery.create_task(sleep_talking("Hello", 10, is_true=True))  # will be ok
    nursery.create_task(sleep_talking("World"))  # will be ok
    nursery.create_task(raise_custom())  # will be silenced as CustomError
    await asyncio.sleep(0.5)

    nursery.create_task(sleep_talking("One!"))  # will be silenced as CancelledError
    nursery.create_task(sleep_talking("Two!"))  # will be silenced as CancelledError
    nursery.create_task(raise_custom())  # will be silenced as CancelledError
    nursery.cleanup_tasks()
    await asyncio.sleep(0.5)

    nursery.create_task(sleep_talking("NoTimeToSpeak!"))  # will be silenced as CancelledError because the loop quits
    nursery.create_task(raise_another_error())  # will be raised immediately as no sleep


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info(f"Running {__file__}")
    logger.info("=" * 80)
    asyncio.run(main())
