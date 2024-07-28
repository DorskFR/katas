import asyncio

from tenacity import RetryCallState, retry
from tenacity.retry import retry_if_exception_type
from tenacity.stop import stop_after_attempt


class CustomError(Exception):
    """Custom error"""


async def sleep_talking(msg: str, number: int | None = None, is_true: bool = False) -> None:
    await asyncio.sleep(0.1)
    print(msg, number, is_true)


def after_print(state: RetryCallState) -> None:
    print(f"Failed {state.attempt_number} time(s)")


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


async def main() -> None:

    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(sleep_talking("Hello", 10, True))
        task2 = tg.create_task(sleep_talking("World"))
        # task2 = tg.create_task(raise_custom())
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
