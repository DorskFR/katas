import asyncio
from typing import Any

import requests
import yarl
from asyncache import cached
from cachetools import TTLCache


@cached(cache=TTLCache(maxsize=1, ttl=10))  # type: ignore[misc]
async def prepare_request(url: str, params: dict[str, Any] | None = None) -> None:
    await asyncio.sleep(0.01)
    req = requests.PreparedRequest()
    req.prepare_url(url, params)
    print(req.url)


async def call_prepare_request_unhashable() -> None:
    url = "http://example.com"
    params = {"color": "blue", "limit": 10, "sort": "true"}
    await asyncio.gather(*[prepare_request(url, params)])


async def call_prepare_request_hashable() -> None:
    url = "http://example.com"
    params = {"color": "blue", "limit": 10, "sort": "true"}
    full_url = str(yarl.URL(url).with_query(params))
    await asyncio.gather(*[prepare_request(full_url)])


async def main() -> None:
    try:
        await call_prepare_request_unhashable()
    except TypeError as error:
        print(error)
    await call_prepare_request_hashable()


if __name__ == "__main__":
    asyncio.run(main())
