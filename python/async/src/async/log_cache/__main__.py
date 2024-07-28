import logging
import time
from collections.abc import Callable
from typing import Any

from cachetools import TTLCache, cached

logger = logging.getLogger(__name__)


def ttl_hash(_lc: Callable[[Any], None], msg: str, *_args: Any, **kwargs: Any) -> str:
    """
    Builds a key from the message and a stable int per interval of time.
    """
    interval: int = kwargs.pop("log_interval", 1)
    timestamp: float | int = time.time() // interval if interval else time.time()
    return f"{msg}{timestamp}"


@cached(TTLCache(maxsize=1024, ttl=3600), key=ttl_hash)  # type: ignore
def suppress_log(
    log_callback: Callable[[Any], None], message: str, *args: Any, **kwargs: Any
) -> None:
    """
    Suppress duplicate logs by using a cache and a key based on the message and the time.
    """
    if "log_interval" in kwargs:
        del kwargs["log_interval"]
    log_callback(message, *args, **kwargs)


def main() -> None:
    for _ in range(1000):
        suppress_log(logger.warning, "first: Message delivery failed", log_interval=5)
    for _ in range(10):
        suppress_log(logger.warning, "second: Message delivery failed", log_interval=0)


if __name__ == "__main__":
    main()
