
from typing import TypedDict

from starlette_api.database.db_client import DatabaseClient


class State(TypedDict):
    db_client: DatabaseClient
