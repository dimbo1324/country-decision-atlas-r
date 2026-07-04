"""Data-quality checks for decision passports: missing snapshots, invalid selected country, missing sources."""

from app.repositories import data_quality as dq_repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality.decision_passport_checks import (
    _append_decision_passport_checks,
)
from psycopg import Connection
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def _install_clean(monkeypatch: Any) -> None:
    for name in [
        "list_active_passports_missing_scenario_slug",
        "list_active_passports_with_empty_candidates",
        "list_active_passports_with_empty_result_snapshot",
        "list_active_passports_with_selected_country_not_in_candidates",
        "list_passports_with_inconsistent_expiry_status",
        "list_active_passports_without_sources",
        "list_old_active_passports_without_expires_at",
    ]:
        monkeypatch.setattr(dq_repository, name, lambda *_: [])


def test_clean_passports_produce_no_issues(monkeypatch: Any) -> None:
    _install_clean(monkeypatch)

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_decision_passport_checks(CONNECTION, issues, checks)

    assert issues == []
    assert all(check.status == "passed" for check in checks)


def test_detects_missing_result_snapshot(monkeypatch: Any) -> None:
    _install_clean(monkeypatch)
    monkeypatch.setattr(
        dq_repository,
        "list_active_passports_with_empty_result_snapshot",
        lambda *_: [{"id": "passport-1"}],
    )

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_decision_passport_checks(CONNECTION, issues, checks)

    critical = [i for i in issues if i.severity == "critical"]
    assert any(
        i.code == "decision_passport_empty_result_snapshot" for i in critical
    )


def test_detects_selected_country_not_in_candidates(monkeypatch: Any) -> None:
    _install_clean(monkeypatch)
    monkeypatch.setattr(
        dq_repository,
        "list_active_passports_with_selected_country_not_in_candidates",
        lambda *_: [{"id": "passport-1", "selected_country_slug": "brazil"}],
    )

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_decision_passport_checks(CONNECTION, issues, checks)

    codes = [i.code for i in issues]
    assert "decision_passport_selected_country_not_candidate" in codes
    critical_codes = [i.code for i in issues if i.severity == "critical"]
    assert "decision_passport_selected_country_not_candidate" in critical_codes


def test_missing_sources_is_warning_not_critical(monkeypatch: Any) -> None:
    _install_clean(monkeypatch)
    monkeypatch.setattr(
        dq_repository,
        "list_active_passports_without_sources",
        lambda *_: [{"id": "passport-1"}],
    )

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_decision_passport_checks(CONNECTION, issues, checks)

    issue = next(
        i for i in issues if i.code == "decision_passport_missing_sources"
    )
    assert issue.severity == "warning"


def test_old_without_expires_at_is_warning(monkeypatch: Any) -> None:
    _install_clean(monkeypatch)
    monkeypatch.setattr(
        dq_repository,
        "list_old_active_passports_without_expires_at",
        lambda *_: [{"id": "passport-1"}],
    )

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_decision_passport_checks(CONNECTION, issues, checks)

    issue = next(
        i for i in issues if i.code == "decision_passport_old_without_expiry"
    )
    assert issue.severity == "warning"
