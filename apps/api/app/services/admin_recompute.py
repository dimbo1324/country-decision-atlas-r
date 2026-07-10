from app.repositories.domain_events import insert_domain_event
from psycopg import Connection
from typing import Any
from uuid import uuid4


def enqueue_recompute_request(
    connection: Connection[Any],
    *,
    resource: str,
    dry_run: bool,
    extra_payload: dict[str, Any] | None = None,
) -> str:
    """Record that an admin asked for a full recompute, instead of looping
    over every country inline in the HTTP request (P2-3, Аудит-эпизод 5).
    notifiable=False keeps this out of the outbox relay entirely (it only
    claims status='pending' AND notifiable=TRUE rows) — this is purely an
    audit record of the request, not a task queue. The loop over all
    countries stays exclusively in scripts/recompute_*.py, run on a
    schedule or by hand; nothing consumes this event to trigger it
    automatically."""
    event_id = uuid4()
    payload: dict[str, Any] = {"resource": resource, "dry_run": dry_run}
    if extra_payload:
        payload.update(extra_payload)
    event = insert_domain_event(
        connection,
        event_key=f"recompute_request:{resource}:{event_id}",
        event_type="recompute_requested",
        aggregate_type="recompute_request",
        aggregate_id=event_id,
        country_slug=None,
        payload=payload,
        status="pending",
        notifiable=False,
    )
    return str(event["id"]) if event else str(event_id)
