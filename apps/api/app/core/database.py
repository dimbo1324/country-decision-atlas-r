from collections.abc import Iterator, Sequence
from typing import Any, cast
from app.core.config import Settings, get_settings
from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
_pool: ConnectionPool[Any] | None = None
def open_database_pool(settings: Settings | None = None) -> None:
    global _pool
    if _pool is not None:
        return
    resolved_settings = settings or get_settings()
    _pool = ConnectionPool(
        conninfo=resolved_settings.database_url,
        kwargs={"row_factory": dict_row},
        min_size=1,
        max_size=10,
        open=False,
    )
    _pool.open()
def close_database_pool() -> None:
    global _pool
    if _pool is None:
        return
    _pool.close()
    _pool = None
def get_pool() -> ConnectionPool[Any]:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized.")
    return _pool
def get_connection() -> Iterator[Connection[Any]]:
    with get_pool().connection() as connection:
        yield connection
def fetch_all(
    connection: Connection[Any],
    query: str,
    params: Sequence[Any] = (),
) -> list[dict[str, Any]]:
    cursor = connection.execute(query, params)
    return cast(list[dict[str, Any]], cursor.fetchall())
def fetch_one(
    connection: Connection[Any],
    query: str,
    params: Sequence[Any] = (),
) -> dict[str, Any] | None:
    cursor = connection.execute(query, params)
    return cast(dict[str, Any] | None, cursor.fetchone())
def execute_one(
    connection: Connection[Any],
    query: str,
    params: Sequence[Any] = (),
) -> dict[str, Any]:
    cursor = connection.execute(query, params)
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError("Expected query to return one row.")
    return cast(dict[str, Any], row)
