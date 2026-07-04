from app.core.errors import api_error
from app.repositories import (
    countries as countries_repository,
    what_changed as repository,
)
from app.schemas.what_changed import (
    WhatChangedItem,
    WhatChangedResponse,
    WhatChangedSummary,
)
from datetime import UTC, datetime, timedelta
from psycopg import Connection
from typing import Any


DEFAULT_DAYS = 30
FETCH_MULTIPLIER = 3

DOMAIN_EVENT_TYPE_MAP: dict[str, str] = {
    "legal_signal.published": "legal_signal_published",
    "route.published": "route_published",
    "drift.changed": "drift_changed",
}

DRIFT_LABEL_TITLES = {
    "negative": "Legal direction changed to negative",
    "mildly_positive": "Legal direction changed to mildly positive",
    "positive": "Legal direction changed to positive",
    "stable": "Legal direction changed to stable",
    "insufficient_data": "Legal direction data became insufficient",
}

DRIFT_IMPORTANCE = {
    "negative": "high",
    "mildly_positive": "medium",
    "positive": "medium",
    "stable": "low",
    "insufficient_data": "low",
}

LEGAL_SIGNAL_IMPORTANCE = {
    "critical": "critical",
    "high": "high",
    "medium": "medium",
    "low": "low",
}


def resolve_since(since: datetime | None, days: int) -> datetime:
    if since is not None:
        return since
    return datetime.now(UTC) - timedelta(days=days)


def _domain_event_item(row: dict[str, Any]) -> dict[str, Any] | None:
    event_type = DOMAIN_EVENT_TYPE_MAP.get(str(row["event_type"]))
    if event_type is None:
        return None
    entity_type = str(row["entity_type"])
    entity_id = str(row["entity_id"])
    country_slug = str(row["country_slug"])
    payload = row.get("payload") or {}
    title = payload.get("title") if isinstance(payload, dict) else None
    if event_type == "route_published":
        summary = "A published route was updated."
        path = f"/routes/{entity_id}"
        importance = "medium"
    elif event_type == "legal_signal_published":
        signal_type = (
            payload.get("signal_type") if isinstance(payload, dict) else None
        )
        summary = (
            f"A published legal signal was updated: {signal_type}."
            if signal_type
            else "A published legal signal was updated."
        )
        path = f"/legal-signals?country_slug={country_slug}"
        impact_level = (
            payload.get("impact_level") if isinstance(payload, dict) else None
        )
        importance = LEGAL_SIGNAL_IMPORTANCE.get(str(impact_level), "medium")
    else:
        summary = "Country legal direction changed based on recent legal signal events."
        path = f"/countries/{country_slug}"
        importance = "medium"
    return {
        "id": str(row["id"]),
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "country_slug": country_slug,
        "title": title or "Data updated",
        "summary": summary,
        "path": path,
        "occurred_at": row["occurred_at"],
        "importance": importance,
        "source": "domain_events",
    }


def _drift_item(row: dict[str, Any]) -> dict[str, Any]:
    label = str(row["label"])
    country_slug = str(row["country_slug"])
    return {
        "id": str(row["id"]),
        "event_type": "drift_changed",
        "entity_type": "country_drift_snapshot",
        "entity_id": str(row["id"]),
        "country_slug": country_slug,
        "title": DRIFT_LABEL_TITLES.get(label, "Legal direction changed"),
        "summary": (
            f"{country_slug.title()}'s legal direction changed based on recent "
            "legal signal events."
        ),
        "path": f"/countries/{country_slug}",
        "occurred_at": row["occurred_at"],
        "importance": DRIFT_IMPORTANCE.get(label, "medium"),
        "source": "country_drift_snapshots",
    }


def _route_item(row: dict[str, Any]) -> dict[str, Any]:
    entity_id = str(row["id"])
    return {
        "id": entity_id,
        "event_type": "route_published",
        "entity_type": "route",
        "entity_id": entity_id,
        "country_slug": str(row["country_slug"]),
        "title": str(row.get("title") or "Route updated"),
        "summary": f"Route information was updated: {row.get('route_type')}.",
        "path": f"/routes/{entity_id}",
        "occurred_at": row["occurred_at"],
        "importance": "medium",
        "source": "routes",
    }


def _legal_signal_item(row: dict[str, Any]) -> dict[str, Any]:
    entity_id = str(row["id"])
    impact_level = str(row.get("impact_level") or "medium")
    return {
        "id": entity_id,
        "event_type": "legal_signal_published",
        "entity_type": "legal_signal",
        "entity_id": entity_id,
        "country_slug": str(row["country_slug"]),
        "title": str(row.get("title") or "Legal signal updated"),
        "summary": f"A published legal signal was updated: {row.get('signal_type')}.",
        "path": f"/legal-signals?country_slug={row['country_slug']}",
        "occurred_at": row["occurred_at"],
        "importance": LEGAL_SIGNAL_IMPORTANCE.get(impact_level, "medium"),
        "source": "legal_signals",
    }


def _deduplicate(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in items:
        key = (item["entity_type"], item["entity_id"], item["event_type"])
        existing = best.get(key)
        if existing is None or item["occurred_at"] > existing["occurred_at"]:
            best[key] = item
    return list(best.values())


def _build_summary(items: list[dict[str, Any]]) -> WhatChangedSummary:
    return WhatChangedSummary(
        total=len(items),
        legal_signals=sum(
            1 for i in items if i["event_type"] == "legal_signal_published"
        ),
        routes=sum(
            1
            for i in items
            if i["event_type"] in {"route_published", "route_updated"}
        ),
        drift=sum(1 for i in items if i["event_type"] == "drift_changed"),
        sources=sum(
            1
            for i in items
            if i["event_type"] in {"source_added", "evidence_added"}
        ),
    )


def build_what_changed(
    connection: Connection[Any],
    country_slug: str,
    locale: str,
    since: datetime | None,
    days: int,
    limit: int,
) -> WhatChangedResponse:
    if (
        countries_repository.get_country(connection, country_slug, locale)
        is None
    ):
        raise api_error(
            404,
            "country_not_found",
            "Country was not found.",
            {"country_slug": country_slug},
        )
    resolved_since = resolve_since(since, days)
    fetch_limit = limit * FETCH_MULTIPLIER

    raw_items: list[dict[str, Any]] = []
    for row in repository.list_country_domain_events_since(
        connection, country_slug, resolved_since, fetch_limit
    ):
        item = _domain_event_item(row)
        if item is not None:
            raw_items.append(item)
    for row in repository.list_country_data_journal_since(
        connection, country_slug, resolved_since, fetch_limit
    ):
        item = _domain_event_item(row)
        if item is not None:
            raw_items.append(item)
    for row in repository.list_country_drift_changes_since(
        connection, country_slug, resolved_since, fetch_limit
    ):
        raw_items.append(_drift_item(row))
    for row in repository.list_country_route_changes_since(
        connection, country_slug, resolved_since, fetch_limit
    ):
        raw_items.append(_route_item(row))
    for row in repository.list_country_legal_signal_changes_since(
        connection, country_slug, resolved_since, fetch_limit
    ):
        raw_items.append(_legal_signal_item(row))

    deduplicated = _deduplicate(raw_items)
    deduplicated.sort(key=lambda item: item["occurred_at"], reverse=True)
    limited = deduplicated[:limit]

    return WhatChangedResponse(
        country_slug=country_slug,
        since=resolved_since,
        generated_at=datetime.now(UTC),
        summary=_build_summary(deduplicated),
        items=[WhatChangedItem(**item) for item in limited],
    )
