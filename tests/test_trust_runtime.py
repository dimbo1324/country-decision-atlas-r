"""Trust score runtime computation: feature-disabled and country-not-found handling, dry-run mode."""

from app.repositories import feature_flags as ff_repo, trust as trust_repo
from app.services.trust_runtime import (
    compute_and_store_trust_for_all_countries,
    compute_and_store_trust_for_country,
)
from datetime import UTC, datetime
import pytest
from typing import Any
from unittest.mock import MagicMock


_NOW = datetime(2025, 6, 1, tzinfo=UTC)

_RICH_INPUTS = {
    "country_id": "country-uuid-1",
    "source_count": 15,
    "evidence_count": 20,
    "legal_signal_count": 8,
    "route_count": 5,
    "platform_metric_count": 3,
    "last_verified_at": datetime(2025, 3, 1, tzinfo=UTC),
    "contradiction_score_value": 10.0,
}

_SPARSE_INPUTS = {
    "country_id": "country-uuid-2",
    "source_count": 2,
    "evidence_count": 1,
    "legal_signal_count": 0,
    "route_count": 0,
    "platform_metric_count": 0,
    "last_verified_at": None,
    "contradiction_score_value": None,
}


def _install_feature_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ff_repo,
        "get_feature_flag",
        lambda *_a: {
            "status": "enabled",
            "access_tier": "public",
            "default_enabled": True,
        },
    )
    monkeypatch.setattr(
        ff_repo,
        "list_feature_access_rules",
        lambda *_a: [{"access_tier": "public", "is_enabled": True}],
    )


def _install_feature_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ff_repo,
        "get_feature_flag",
        lambda *_a: {
            "status": "disabled",
            "access_tier": "public",
            "default_enabled": False,
        },
    )
    monkeypatch.setattr(
        ff_repo,
        "list_feature_access_rules",
        lambda *_a: [{"access_tier": "public", "is_enabled": False}],
    )


def test_returns_feature_disabled_when_flag_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_feature_disabled(monkeypatch)
    conn = MagicMock()
    result = compute_and_store_trust_for_country(conn, "russia", now=_NOW)
    assert result["feature_enabled"] is False
    assert result["computed"] is False


def test_returns_country_not_found_when_inputs_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_feature_enabled(monkeypatch)
    monkeypatch.setattr(trust_repo, "get_trust_inputs_for_country", lambda *_: None)
    conn = MagicMock()
    result = compute_and_store_trust_for_country(conn, "nonexistent", now=_NOW)
    assert result["country_not_found"] is True
    assert result["computed"] is False


def test_computes_trust_with_rich_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_feature_enabled(monkeypatch)
    monkeypatch.setattr(
        trust_repo, "get_trust_inputs_for_country", lambda *_: _RICH_INPUTS
    )
    stored: list[dict[str, Any]] = []
    monkeypatch.setattr(
        trust_repo, "upsert_country_trust_score", lambda _conn, p: stored.append(p)
    )
    conn = MagicMock()
    result = compute_and_store_trust_for_country(conn, "russia", now=_NOW)
    assert result["computed"] is True
    assert result["stored"] is True
    assert result.get("error") is None
    assert "trust_label" in result
    assert "trust_score" in result


def test_dry_run_does_not_store(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_feature_enabled(monkeypatch)
    monkeypatch.setattr(
        trust_repo, "get_trust_inputs_for_country", lambda *_: _RICH_INPUTS
    )
    stored: list[Any] = []
    monkeypatch.setattr(
        trust_repo, "upsert_country_trust_score", lambda _conn, p: stored.append(p)
    )
    conn = MagicMock()
    result = compute_and_store_trust_for_country(conn, "russia", now=_NOW, dry_run=True)
    assert result["computed"] is True
    assert result["stored"] is False
    assert len(stored) == 0


def test_insufficient_data_still_computes(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_feature_enabled(monkeypatch)
    monkeypatch.setattr(
        trust_repo, "get_trust_inputs_for_country", lambda *_: _SPARSE_INPUTS
    )
    monkeypatch.setattr(trust_repo, "upsert_country_trust_score", lambda *_: None)
    conn = MagicMock()
    result = compute_and_store_trust_for_country(conn, "russia", now=_NOW)
    assert result["computed"] is True
    assert result["trust_label"] == "insufficient_data"
    assert result["trust_score"] is None


def test_all_countries_feature_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_feature_disabled(monkeypatch)
    conn = MagicMock()
    summary = compute_and_store_trust_for_all_countries(conn, now=_NOW)
    assert summary["feature_enabled"] is False
    assert summary["countries_processed"] == 0


def test_all_countries_processes_each(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_feature_enabled(monkeypatch)
    countries = [
        {"id": "id-1", "slug": "russia"},
        {"id": "id-2", "slug": "uruguay"},
    ]
    monkeypatch.setattr(trust_repo, "list_active_countries", lambda *_: countries)
    inputs_by_slug = {"russia": _RICH_INPUTS, "uruguay": _SPARSE_INPUTS}
    monkeypatch.setattr(
        trust_repo,
        "get_trust_inputs_for_country",
        lambda _conn, slug: dict(inputs_by_slug.get(slug, _SPARSE_INPUTS)),
    )
    monkeypatch.setattr(trust_repo, "upsert_country_trust_score", lambda *_: None)
    conn = MagicMock()
    summary = compute_and_store_trust_for_all_countries(conn, now=_NOW)
    assert summary["countries_processed"] == 2
    assert summary["countries_computed"] == 2
    assert summary["countries_failed"] == 0
    assert summary["errors"] == []
