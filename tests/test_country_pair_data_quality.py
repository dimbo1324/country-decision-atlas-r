from app.repositories import data_quality as dq_repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality.country_pair_checks import _append_country_pair_checks
from psycopg import Connection
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_detects_pair_without_sources(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        dq_repository,
        "list_published_pairs_without_sources",
        lambda *_: [
            {"id": "pair-1", "origin_slug": "russia", "destination_slug": "uruguay"}
        ],
    )
    monkeypatch.setattr(
        dq_repository, "list_published_pairs_missing_last_verified_at", lambda *_: []
    )
    monkeypatch.setattr(dq_repository, "list_stale_published_pairs", lambda *_: [])

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_country_pair_checks(CONNECTION, issues, checks)

    codes = [issue.code for issue in issues]
    assert "country_pair_missing_source" in codes
    check = next(c for c in checks if c.code == "country_pairs_have_sources")
    assert check.status == "failed"


def test_detects_pair_missing_last_verified_at(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        dq_repository, "list_published_pairs_without_sources", lambda *_: []
    )
    monkeypatch.setattr(
        dq_repository,
        "list_published_pairs_missing_last_verified_at",
        lambda *_: [
            {"id": "pair-1", "origin_slug": "russia", "destination_slug": "uruguay"}
        ],
    )
    monkeypatch.setattr(dq_repository, "list_stale_published_pairs", lambda *_: [])

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_country_pair_checks(CONNECTION, issues, checks)

    codes = [issue.code for issue in issues]
    assert "country_pair_missing_last_verified_at" in codes


def test_stale_pair_is_warning_not_critical(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        dq_repository, "list_published_pairs_without_sources", lambda *_: []
    )
    monkeypatch.setattr(
        dq_repository, "list_published_pairs_missing_last_verified_at", lambda *_: []
    )
    monkeypatch.setattr(
        dq_repository,
        "list_stale_published_pairs",
        lambda *_: [
            {
                "id": "pair-1",
                "origin_slug": "russia",
                "destination_slug": "uruguay",
                "freshness_status": "stale",
            }
        ],
    )

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_country_pair_checks(CONNECTION, issues, checks)

    stale_issue = next(i for i in issues if i.code == "country_pair_stale")
    assert stale_issue.severity == "warning"


def test_passes_when_all_pairs_healthy(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        dq_repository, "list_published_pairs_without_sources", lambda *_: []
    )
    monkeypatch.setattr(
        dq_repository, "list_published_pairs_missing_last_verified_at", lambda *_: []
    )
    monkeypatch.setattr(dq_repository, "list_stale_published_pairs", lambda *_: [])

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_country_pair_checks(CONNECTION, issues, checks)

    assert all(check.status == "passed" for check in checks)
    assert issues == []
