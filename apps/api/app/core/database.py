from app.core.config import Settings, get_settings
from collections.abc import Iterator, Sequence
from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from typing import Any, cast


_pool: ConnectionPool[Any] | None = None
_readiness_pool: ConnectionPool[Any] | None = None

# Deliberately tiny and fixed (not env-configurable like the main pool):
# /ready must fail fast on its own short queue rather than wait behind
# request traffic saturating the main pool (P3-6, Аудит-эпизод 10).
_READINESS_POOL_MIN_SIZE = 1
_READINESS_POOL_MAX_SIZE = 2
_READINESS_POOL_TIMEOUT_SECONDS = 5.0


def open_database_pool(settings: Settings | None = None) -> None:
    global _pool
    if _pool is not None:
        return
    resolved_settings = settings or get_settings()
    _pool = ConnectionPool(
        conninfo=resolved_settings.database_url,
        kwargs={"row_factory": dict_row},
        min_size=resolved_settings.database_pool_min_size,
        max_size=resolved_settings.database_pool_max_size,
        timeout=resolved_settings.database_pool_timeout_seconds,
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


def open_readiness_pool(settings: Settings | None = None) -> None:
    """Separate, tiny connection pool used only by /ready (P3-6).

    Keeping this isolated from the main pool means readiness checks don't
    queue behind saturated request traffic and report a healthy instance
    as unready, which could trigger an orchestrator restart.
    """
    global _readiness_pool
    if _readiness_pool is not None:
        return
    resolved_settings = settings or get_settings()
    _readiness_pool = ConnectionPool(
        conninfo=resolved_settings.database_url,
        kwargs={"row_factory": dict_row},
        min_size=_READINESS_POOL_MIN_SIZE,
        max_size=_READINESS_POOL_MAX_SIZE,
        timeout=_READINESS_POOL_TIMEOUT_SECONDS,
        open=False,
    )
    _readiness_pool.open()


def close_readiness_pool() -> None:
    global _readiness_pool
    if _readiness_pool is None:
        return
    _readiness_pool.close()
    _readiness_pool = None


def get_readiness_pool() -> ConnectionPool[Any]:
    if _readiness_pool is None:
        raise RuntimeError("Readiness database pool is not initialized.")
    return _readiness_pool


def get_pool_stats() -> dict[str, int]:
    """Exposes ConnectionPool.get_stats() (pool_size, pool_available,
    requests_waiting, etc.) for a future /metrics endpoint (P2-4, Аудит-
    эпизод 6; see AE-7 for the endpoint itself)."""
    return get_pool().get_stats()


def get_connection() -> Iterator[Connection[Any]]:
    """Yield a pooled connection that commits or rolls back on its own.

    `ConnectionPool.connection()` commits the transaction when this context
    manager exits cleanly and rolls back if an exception propagates out of
    the request handler. Explicit `connection.commit()` calls in routers are
    therefore redundant but harmless; see P2-9, Аудит-эпизод 4 in
    docs/_arch_/09_План_устранения_аудита.md for the decision record.
    """
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
