from app.api.v1 import country_drift as country_drift_api
from app.repositories import country_drift as country_drift_repo
from datetime import UTC, date, datetime
from fastapi import HTTPException
from psycopg import Connection
import pytest
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())

_COUNTRY = {
    "id": "11111111-1111-1111-1111-111111111111",
    "slug": "argentina",
    "name": "Argentina",
}

_SNAPSHOT_ROW = {
    "id": "snap-1",
    "country_id": "11111111-1111-1111-1111-111111111111",
    "country_slug": "argentina",
    "period_start": date(2026, 1, 1),
    "period_end": date(2026, 6, 30),
    "window_days": 180,
    "label": "mildly_positive",
    "previous_label": "stable",
    "confidence": "medium",
    "net_score": 27.5,
    "positive_weight": 8.0,
    "negative_weight": 3.0,
    "neutral_weight": 1.0,
    "mixed_weight": 0.0,
    "uncertain_weight": 0.0,
    "total_weight": 12.0,
    "event_count": 6,
    "positive_count": 3,
    "negative_count": 1,
    "neutral_count": 2,
    "mixed_count": 0,
    "uncertain_count": 0,
    "methodology_version": "v1.0",
    "input_summary": {"window_days": 180},
    "computed_at": datetime(2026, 7, 1, tzinfo=UTC),
    "expires_at": None,
}


def test_get_country_drift_returns_latest_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        country_drift_repo, "get_country_for_drift", lambda *_: _COUNTRY
    )
    monkeypatch.setattr(
        country_drift_repo, "get_latest_drift_snapshot", lambda *_: _SNAPSHOT_ROW
    )
    monkeypatch.setattr(
        country_drift_repo, "list_drift_snapshots", lambda *_a, **_kw: [_SNAPSHOT_ROW]
    )
    result = country_drift_api.get_country_drift("argentina", CONNECTION)
    assert result.country_slug == "argentina"
    assert result.latest_snapshot is not None
    assert result.latest_snapshot.label == "mildly_positive"
    assert result.latest_snapshot.net_score == pytest.approx(27.5)


def test_get_country_drift_returns_history(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        country_drift_repo, "get_country_for_drift", lambda *_: _COUNTRY
    )
    monkeypatch.setattr(
        country_drift_repo, "get_latest_drift_snapshot", lambda *_: _SNAPSHOT_ROW
    )
    monkeypatch.setattr(
        country_drift_repo, "list_drift_snapshots", lambda *_a, **_kw: [_SNAPSHOT_ROW]
    )
    result = country_drift_api.get_country_drift("argentina", CONNECTION)
    assert len(result.history) == 1
    assert result.history[0].label == "mildly_positive"


def test_get_country_drift_returns_404_for_unknown_country(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(country_drift_repo, "get_country_for_drift", lambda *_: None)
    with pytest.raises(HTTPException) as exc:
        country_drift_api.get_country_drift("nowhere", CONNECTION)
    assert exc.value.status_code == 404


def test_get_country_drift_returns_controlled_empty_response_when_no_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        country_drift_repo, "get_country_for_drift", lambda *_: _COUNTRY
    )
    monkeypatch.setattr(
        country_drift_repo, "get_latest_drift_snapshot", lambda *_: None
    )
    monkeypatch.setattr(
        country_drift_repo, "list_drift_snapshots", lambda *_a, **_kw: []
    )
    result = country_drift_api.get_country_drift("argentina", CONNECTION)
    assert result.latest_snapshot is None
    assert result.history == []


def test_get_country_drift_disclaimer_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        country_drift_repo, "get_country_for_drift", lambda *_: _COUNTRY
    )
    monkeypatch.setattr(
        country_drift_repo, "get_latest_drift_snapshot", lambda *_: None
    )
    monkeypatch.setattr(
        country_drift_repo, "list_drift_snapshots", lambda *_a, **_kw: []
    )
    result = country_drift_api.get_country_drift("argentina", CONNECTION)
    assert "not" in result.disclaimer.lower()
