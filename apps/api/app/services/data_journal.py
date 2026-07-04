from app.core.errors import api_error
from app.repositories import (
    countries as countries_repository,
    data_journal as repository,
)
from app.schemas.data_journal import (
    CountryDataJournalResponse,
    DataJournalEntry,
)
from psycopg import Connection
from typing import Any


EVENT_TYPE_MAP = {
    "legal_signal.published": "legal_signal_published",
    "legal_signal_event.published": "legal_signal_published",
    "route.published": "route_published",
    "user_story.published": "data_reviewed",
}


def build_country_data_journal(
    connection: Connection[Any],
    country_slug: str,
    locale: str,
    limit: int,
    offset: int,
) -> CountryDataJournalResponse:
    if (
        countries_repository.get_country(connection, country_slug, locale)
        is None
    ):
        raise api_error(
            404,
            "country_not_found",
            "Country not found.",
            {"country_slug": country_slug},
        )
    rows = repository.list_country_data_journal_entries(
        connection, country_slug, limit, offset
    )
    total = repository.count_country_data_journal_entries(
        connection, country_slug
    )
    verified = repository.get_country_last_verified_at(connection, country_slug)
    return CountryDataJournalResponse(
        country_slug=country_slug,
        locale=locale,
        items=[_entry(row, locale) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
        last_verified_at=verified.get("last_verified_at") if verified else None,
    )


def sanitize_audit_entry(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in row.items()
        if key
        not in {
            "changed_by",
            "changes",
            "metadata",
            "status",
            "delivery_status",
            "last_error",
            "attempts",
        }
    }


def public_title_for_event(
    event_type: str, payload: dict[str, Any], locale: str
) -> str:
    title = payload.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()[:160]
    if event_type == "route.published":
        return "Маршрут обновлён" if locale == "ru" else "Route updated"
    if event_type in {"legal_signal.published", "legal_signal_event.published"}:
        return (
            "Правовой сигнал обновлён"
            if locale == "ru"
            else "Legal signal updated"
        )
    return "Данные обновлены" if locale == "ru" else "Data updated"


def public_summary_for_event(
    event_type: str, payload: dict[str, Any], locale: str
) -> str:
    if event_type == "route.published":
        route_type = payload.get("route_type")
        if isinstance(route_type, str) and route_type:
            return (
                f"Опубликована обновлённая информация по маршруту: {route_type}."
                if locale == "ru"
                else f"Updated public route information was published: {route_type}."
            )
    if event_type in {"legal_signal.published", "legal_signal_event.published"}:
        signal_type = payload.get("signal_type")
        if isinstance(signal_type, str) and signal_type:
            return (
                f"Опубликован обновлённый правовой сигнал: {signal_type}."
                if locale == "ru"
                else f"Updated public legal signal information was published: {signal_type}."
            )
    return (
        "Публичные данные по стране обновлены и проходят source-backed редакционный процесс."
        if locale == "ru"
        else "Public country data was updated through the source-backed editorial process."
    )


def _entry(row: dict[str, Any], locale: str) -> DataJournalEntry:
    safe = sanitize_audit_entry(row)
    payload = safe.get("payload")
    safe_payload = payload if isinstance(payload, dict) else {}
    event_type = str(safe["event_type"])
    return DataJournalEntry(
        id=str(safe["id"]),
        entry_type=EVENT_TYPE_MAP.get(event_type, "data_reviewed"),
        country_slug=str(safe["country_slug"]),
        entity_type=str(safe["entity_type"]),
        entity_id=str(safe["entity_id"]),
        title=public_title_for_event(event_type, safe_payload, locale),
        summary=public_summary_for_event(event_type, safe_payload, locale),
        event_date=safe["event_date"],
        source=str(safe["source"]),
        is_source_backed=bool(safe["is_source_backed"]),
        last_verified_at=safe.get("last_verified_at"),
    )
