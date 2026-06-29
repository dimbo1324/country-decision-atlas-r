from app.core.database import fetch_all, fetch_one
from collections.abc import Mapping
import json
from psycopg import Connection
from typing import Any
from uuid import UUID


def insert_analytics_event(
    conn: Connection[Any],
    *,
    session_hash: str,
    event_type: str,
    source: str,
    path: str | None,
    locale: str | None,
    country_slug: str | None,
    scenario_slug: str | None,
    persona_slug: str | None,
    route_id: UUID | None,
    entity_type: str | None,
    entity_id: UUID | None,
    metadata: Mapping[str, Any],
) -> UUID:
    row = fetch_one(
        conn,
        """
        INSERT INTO analytics_events (
            session_hash,
            event_type,
            source,
            path,
            locale,
            country_slug,
            scenario_slug,
            persona_slug,
            route_id,
            entity_type,
            entity_id,
            metadata
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s::uuid,
            %s,
            %s::uuid,
            %s::jsonb
        )
        RETURNING id
        """,
        (
            session_hash,
            event_type,
            source,
            path,
            locale,
            country_slug,
            scenario_slug,
            persona_slug,
            str(route_id) if route_id is not None else None,
            entity_type,
            str(entity_id) if entity_id is not None else None,
            json.dumps(dict(metadata), default=str),
        ),
    )
    if row is None:
        raise RuntimeError("Expected analytics_events insert to return id.")
    return UUID(str(row["id"]))


def count_analytics_events(conn: Connection[Any]) -> int:
    row = fetch_one(conn, "SELECT COUNT(*) AS cnt FROM analytics_events", ())
    if row is None:
        return 0
    return int(row["cnt"])


def count_analytics_events_by_type(
    conn: Connection[Any],
    event_type: str,
) -> int:
    row = fetch_one(
        conn,
        "SELECT COUNT(*) AS cnt FROM analytics_events WHERE event_type = %s",
        (event_type,),
    )
    if row is None:
        return 0
    return int(row["cnt"])


def get_latest_analytics_events(
    conn: Connection[Any],
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    safe_limit = max(1, min(limit, 100))
    return fetch_all(
        conn,
        """
        SELECT
            id,
            session_hash,
            event_type,
            source,
            path,
            locale,
            country_slug,
            scenario_slug,
            persona_slug,
            route_id,
            entity_type,
            entity_id,
            metadata,
            created_at
        FROM analytics_events
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (safe_limit,),
    )
