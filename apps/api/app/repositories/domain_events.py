import json
from app.core.database import fetch_all, fetch_one
from collections.abc import Mapping
from psycopg import Connection
from typing import Any
from uuid import UUID


def insert_domain_event(
    conn: Connection[Any],
    *,
    event_key: str,
    event_type: str,
    aggregate_type: str,
    aggregate_id: UUID,
    country_slug: str | None,
    payload: Mapping[str, Any],
    status: str = "pending",
    notifiable: bool = True,
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        """
        INSERT INTO domain_events (
            event_key,
            event_type,
            aggregate_type,
            aggregate_id,
            country_slug,
            payload,
            status,
            notifiable
        )
        VALUES (%s, %s, %s, %s::uuid, %s, %s::jsonb, %s, %s)
        ON CONFLICT (event_key) DO NOTHING
        RETURNING
            id,
            event_key,
            event_type,
            aggregate_type,
            aggregate_id,
            country_slug,
            payload,
            status,
            notifiable,
            created_at,
            relayed_at,
            attempts,
            last_error
        """,
        (
            event_key,
            event_type,
            aggregate_type,
            str(aggregate_id),
            country_slug,
            json.dumps(dict(payload), default=str),
            status,
            notifiable,
        ),
    )


def count_domain_events(conn: Connection[Any]) -> int:
    row = fetch_one(conn, "SELECT COUNT(*) AS cnt FROM domain_events", ())
    if row is None:
        return 0
    return int(row["cnt"])


def count_pending_notifiable_events(conn: Connection[Any]) -> int:
    row = fetch_one(
        conn,
        "SELECT COUNT(*) AS cnt FROM domain_events WHERE status = 'pending' AND notifiable = TRUE",
        (),
    )
    if row is None:
        return 0
    return int(row["cnt"])


def list_pending_domain_events(
    conn: Connection[Any],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT
            id,
            event_key,
            event_type,
            aggregate_type,
            aggregate_id,
            country_slug,
            payload,
            status,
            notifiable,
            created_at,
            relayed_at,
            attempts,
            last_error
        FROM domain_events
        WHERE status = 'pending'
          AND notifiable = TRUE
        ORDER BY created_at ASC
        LIMIT %s
        """,
        (limit,),
    )


def mark_domain_event_relayed(
    conn: Connection[Any],
    event_id: UUID,
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        """
        UPDATE domain_events
        SET status = 'relayed', relayed_at = NOW()
        WHERE id = %s::uuid
        RETURNING
            id, event_key, event_type, aggregate_type, aggregate_id,
            country_slug, payload, status, notifiable, created_at,
            relayed_at, attempts, last_error
        """,
        (str(event_id),),
    )


def mark_domain_event_failed(
    conn: Connection[Any],
    event_id: UUID,
    error: str,
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        """
        UPDATE domain_events
        SET status = 'failed', attempts = attempts + 1, last_error = %s
        WHERE id = %s::uuid
        RETURNING
            id, event_key, event_type, aggregate_type, aggregate_id,
            country_slug, payload, status, notifiable, created_at,
            relayed_at, attempts, last_error
        """,
        (error, str(event_id)),
    )


def mark_domain_event_skipped(
    conn: Connection[Any],
    event_id: UUID,
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        """
        UPDATE domain_events
        SET status = 'skipped'
        WHERE id = %s::uuid
        RETURNING
            id, event_key, event_type, aggregate_type, aggregate_id,
            country_slug, payload, status, notifiable, created_at,
            relayed_at, attempts, last_error
        """,
        (str(event_id),),
    )


def lock_pending_notifiable_domain_events(
    conn: Connection[Any],
    *,
    batch_size: int,
    notify_after: str,
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT
            id,
            event_key,
            event_type,
            aggregate_type,
            aggregate_id,
            country_slug,
            payload,
            status,
            notifiable,
            created_at,
            relayed_at,
            attempts,
            last_error
        FROM domain_events
        WHERE status = 'pending'
          AND notifiable = TRUE
          AND created_at >= %s::timestamptz
        ORDER BY created_at ASC
        LIMIT %s
        FOR UPDATE SKIP LOCKED
        """,
        (notify_after, batch_size),
    )


def lock_and_mark_in_flight_domain_events(
    conn: Connection[Any],
    *,
    batch_size: int,
    notify_after: str,
) -> list[dict[str, Any]]:
    """Claim a batch of pending events for relay in one short transaction.

    Selecting with FOR UPDATE SKIP LOCKED and marking status='in_flight' in
    the same transaction lets the caller commit and release row locks
    immediately, before making the blocking publish call. See P1-1,
    Аудит-эпизод 4.
    """
    locked = fetch_all(
        conn,
        """
        SELECT id
        FROM domain_events
        WHERE status = 'pending'
          AND notifiable = TRUE
          AND created_at >= %s::timestamptz
        ORDER BY created_at ASC
        LIMIT %s
        FOR UPDATE SKIP LOCKED
        """,
        (notify_after, batch_size),
    )
    if not locked:
        return []
    ids = [row["id"] for row in locked]
    return fetch_all(
        conn,
        """
        UPDATE domain_events
        SET status = 'in_flight', locked_at = NOW()
        WHERE id = ANY(%s)
        RETURNING
            id,
            event_key,
            event_type,
            aggregate_type,
            aggregate_id,
            country_slug,
            payload,
            status,
            notifiable,
            created_at,
            relayed_at,
            attempts,
            last_error
        """,
        (ids,),
    )


def requeue_stale_in_flight_domain_events(
    conn: Connection[Any],
    *,
    stale_after_seconds: int,
) -> int:
    """Recover events stuck in_flight by a relay process that crashed mid-publish."""
    rows = fetch_all(
        conn,
        """
        UPDATE domain_events
        SET status = 'pending', locked_at = NULL
        WHERE status = 'in_flight'
          AND locked_at < NOW() - (%s || ' seconds')::interval
        RETURNING id
        """,
        (stale_after_seconds,),
    )
    return len(rows)


def mark_domain_event_publish_failed_or_retry(
    conn: Connection[Any],
    event_id: UUID,
    error: str,
    max_attempts: int,
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        """
        UPDATE domain_events
        SET
            attempts = attempts + 1,
            last_error = %s,
            status = CASE WHEN attempts + 1 >= %s THEN 'failed' ELSE 'pending' END
        WHERE id = %s::uuid
        RETURNING
            id, event_key, event_type, aggregate_type, aggregate_id,
            country_slug, payload, status, notifiable, created_at,
            relayed_at, attempts, last_error
        """,
        (error, max_attempts, str(event_id)),
    )


def list_invalid_domain_events_for_dq(
    conn: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT
            id, event_key, event_type, aggregate_type, aggregate_id,
            payload, status, created_at
        FROM domain_events
        WHERE
            COALESCE(BTRIM(event_key), '') = ''
            OR COALESCE(BTRIM(event_type), '') = ''
            OR COALESCE(BTRIM(aggregate_type), '') = ''
            OR aggregate_id IS NULL
            OR payload IS NULL
        """,
        (),
    )
