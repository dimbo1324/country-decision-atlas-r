from app.repositories import legal_signal_events
from psycopg import Connection
from typing import Any


def list_latest_legal_events(
    connection: Connection[Any], limit: int = 5
) -> list[dict[str, Any]]:
    return legal_signal_events.list_timeline_events(
        connection,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        limit,
        0,
    )
