from app.repositories import legal_signal_events as repository
from app.repositories.common import build_locale
from app.schemas.legal_signal_events import (
    LegalSignalTimelineResponse,
    TimelineFilters,
    TimelineYearGroup,
)
from app.services.localization import overlay_localized_fields
from psycopg import Connection
from typing import Any


def build_timeline_response(
    connection: Connection[Any],
    locale: str,
    country_slug: str | None,
    signal_type: str | None,
    impact_direction: str | None,
    impact_level: str | None,
    affected_group: str | None,
    year_from: int | None,
    year_to: int | None,
    limit: int,
    offset: int,
) -> LegalSignalTimelineResponse:
    if country_slug and not repository.country_exists(connection, country_slug):
        raise LookupError("Country not found")
    rows = repository.list_timeline_events(
        connection,
        country_slug,
        signal_type,
        impact_direction,
        impact_level,
        affected_group,
        year_from,
        year_to,
        limit,
        offset,
    )
    rows = overlay_localized_fields(
        connection,
        rows,
        "legal_signal",
        "legal_signal_id",
        [
            ("title", "title", "title_ru", "title_en"),
            ("summary", "summary", "summary_ru", "summary_en"),
        ],
        locale,
    )
    groups: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        row["legal_signal_title"] = row["title"]
        row["source"] = _source(row)
        row["evidence"] = _evidence(row)
        row["quality_warnings"] = _warnings(row)
        groups.setdefault(int(row["event_year"]), []).append(row)
    total = repository.count_timeline_events(
        connection,
        country_slug,
        signal_type,
        impact_direction,
        impact_level,
        affected_group,
        year_from,
        year_to,
    )
    return LegalSignalTimelineResponse(
        locale=build_locale(rows, locale),
        filters=TimelineFilters(
            country_slug=country_slug,
            signal_type=signal_type,
            impact_direction=impact_direction,
            impact_level=impact_level,
            affected_group=affected_group,
            year_from=year_from,
            year_to=year_to,
        ),
        groups=[
            TimelineYearGroup(year=year, events=events)
            for year, events in sorted(groups.items(), reverse=True)
        ],
        total=total,
        limit=limit,
        offset=offset,
        available_years=repository.list_timeline_years(connection, country_slug),
    )


def _source(row: dict[str, Any]) -> dict[str, Any] | None:
    if not row.get("source_ref_id"):
        return None
    return {
        "id": row["source_ref_id"],
        "title": row["source_title"],
        "url": row["source_url"],
        "publisher": row.get("source_publisher"),
        "source_type": row["source_type"],
        "confidence": row.get("source_confidence"),
    }


def _evidence(row: dict[str, Any]) -> dict[str, Any] | None:
    if not row.get("evidence_ref_id"):
        return None
    return {
        "id": row["evidence_ref_id"],
        "claim": row["evidence_claim"],
        "excerpt": row.get("evidence_excerpt"),
        "url": row.get("evidence_url"),
        "confidence": row.get("evidence_confidence"),
    }


def _warnings(row: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if not row.get("source_ref_id"):
        warnings.append("source_missing")
    if not row.get("evidence_ref_id"):
        warnings.append("evidence_missing")
    return warnings
