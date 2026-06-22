from app.services.legal_signal_timeline import build_timeline_response
from datetime import date
from pathlib import Path
import pytest
from tests.test_openapi_contract import load_contract
from typing import Any
from unittest.mock import MagicMock, patch


MIGRATION_SQL = Path("database/migrations/019_legal_signals_timeline_v1.sql").read_text(
    encoding="utf-8"
)
CONNECTION = MagicMock()


def event_row(**overrides: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": "11111111-1111-4111-8111-111111111111",
        "legal_signal_id": "22222222-2222-4222-8222-222222222222",
        "country_id": "33333333-3333-4333-8333-333333333333",
        "country_slug": "russia",
        "country_name": "Russia",
        "event_date": date(2025, 6, 1),
        "event_year": 2025,
        "event_type": "confirmed",
        "impact_direction": "negative",
        "impact_level": "high",
        "affected_groups": ["migrants"],
        "title": "Signal title",
        "summary": "Signal summary",
        "signal_type": "policy",
        "title_ru": "Сигнал",
        "title_en": "Signal title",
        "summary_ru": "Описание",
        "summary_en": "Signal summary",
        "source_ref_id": "44444444-4444-4444-8444-444444444444",
        "source_title": "Official source",
        "source_url": "https://government.example/source",
        "source_publisher": "Government",
        "source_type": "official",
        "source_confidence": "high",
        "evidence_ref_id": "55555555-5555-4555-8555-555555555555",
        "evidence_claim": "Confirmed claim",
        "evidence_excerpt": "Excerpt",
        "evidence_url": "https://government.example/evidence",
        "evidence_confidence": "high",
        "translation_status": "source",
        "resolved_locale": "en",
        "localization": None,
    }
    row.update(overrides)
    return row


def build(rows: list[dict[str, Any]], **filters: Any) -> Any:
    with (
        patch(
            "app.services.legal_signal_timeline.repository.country_exists",
            return_value=True,
        ),
        patch(
            "app.services.legal_signal_timeline.repository.list_timeline_events",
            return_value=rows,
        ),
        patch(
            "app.services.legal_signal_timeline.repository.count_timeline_events",
            return_value=len(rows),
        ),
        patch(
            "app.services.legal_signal_timeline.repository.list_timeline_years",
            return_value=[2026, 2025],
        ),
        patch(
            "app.services.legal_signal_timeline.overlay_localized_fields",
            side_effect=lambda _c, items, *_a: items,
        ),
    ):
        return build_timeline_response(
            CONNECTION,
            filters.get("locale", "en"),
            filters.get("country_slug"),
            filters.get("signal_type"),
            filters.get("impact_direction"),
            filters.get("impact_level"),
            filters.get("affected_group"),
            filters.get("year_from"),
            filters.get("year_to"),
            50,
            0,
        )


def test_timeline_groups_events_by_year_in_repository_order() -> None:
    result = build(
        [
            event_row(event_year=2026, event_date=date(2026, 2, 1)),
            event_row(event_year=2025),
        ]
    )

    assert [group.year for group in result.groups] == [2026, 2025]
    assert result.total == 2


def test_timeline_exposes_source_and_evidence() -> None:
    event = build([event_row()]).groups[0].events[0]

    assert event.source is not None
    assert event.source.publisher == "Government"
    assert event.evidence is not None
    assert event.evidence.claim == "Confirmed claim"


def test_event_without_evidence_does_not_crash() -> None:
    event = build([event_row(evidence_ref_id=None)]).groups[0].events[0]

    assert event.evidence is None
    assert event.quality_warnings == ["evidence_missing"]


def test_event_without_source_or_evidence_has_quality_warnings() -> None:
    event = (
        build([event_row(source_ref_id=None, evidence_ref_id=None)]).groups[0].events[0]
    )

    assert event.quality_warnings == ["source_missing", "evidence_missing"]


def test_timeline_preserves_filter_metadata() -> None:
    result = build(
        [event_row()],
        country_slug="russia",
        impact_direction="negative",
        impact_level="high",
        signal_type="policy",
        year_from=2025,
        year_to=2025,
    )

    assert result.filters.country_slug == "russia"
    assert result.filters.impact_direction == "negative"
    assert result.filters.impact_level == "high"
    assert result.filters.signal_type == "policy"
    assert result.filters.year_from == 2025


def test_unknown_country_returns_clean_not_found() -> None:
    with (
        patch(
            "app.services.legal_signal_timeline.repository.country_exists",
            return_value=False,
        ),
        pytest.raises(LookupError, match="Country not found"),
    ):
        build_timeline_response(
            CONNECTION, "en", "unknown", None, None, None, None, None, None, 50, 0
        )


def test_empty_timeline_is_stable() -> None:
    result = build([])

    assert result.groups == []
    assert result.total == 0


def test_localization_metadata_does_not_crash() -> None:
    result = build([event_row()], locale="ru")

    assert result.locale.requested_locale == "ru"


def test_repository_sql_uses_parameterized_filters_and_expected_sorting() -> None:
    from app.repositories import legal_signal_events

    with patch.object(legal_signal_events, "fetch_all", return_value=[]) as fetch:
        legal_signal_events.list_timeline_events(
            CONNECTION,
            "russia",
            "policy",
            "negative",
            "high",
            "migrants",
            2024,
            2026,
            50,
            0,
        )

    query = fetch.call_args.args[1]
    params = fetch.call_args.args[2]
    assert "c.slug = %s" in query
    assert "lse.affected_groups ? %s" in query
    assert "lse.event_date DESC" in query
    assert params[-2:] == (50, 0)


def test_migration_is_additive_idempotent_and_source_backed() -> None:
    assert "CREATE TABLE IF NOT EXISTS legal_signal_events" in MIGRATION_SQL
    assert (
        "ON CONFLICT (legal_signal_id, event_date, event_type) DO UPDATE"
        in MIGRATION_SQL
    )
    assert "DROP TABLE" not in MIGRATION_SQL
    assert "DELETE FROM" not in MIGRATION_SQL
    assert "LEFT JOIN LATERAL" in MIGRATION_SQL
    assert "ls.source_id" in MIGRATION_SQL
    assert "'confirmed'" in MIGRATION_SQL


def test_openapi_has_timeline_endpoint_and_schemas() -> None:
    contract = load_contract()

    assert "/api/v1/legal-signals/timeline" in contract["paths"]
    for name in [
        "LegalSignalTimelineEvent",
        "LegalSignalTimelineResponse",
        "TimelineYearGroup",
        "TimelineFilters",
        "TimelineSourceRef",
        "TimelineEvidenceRef",
    ]:
        assert name in contract["components"]["schemas"]
