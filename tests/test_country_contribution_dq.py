"""Data-quality checks for country contribution: curator required, curator role valid, published country active."""

from app.repositories import data_quality as data_quality_repository
from app.services import data_quality
from app.services.data_quality.country_contribution_checks import (
    _append_country_contribution_checks,
)
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_clean_state_produces_no_critical_country_contribution_issues(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    report = data_quality.build_data_quality_report(CONNECTION)
    codes = {check.code for check in report.checks}
    assert "country_proposals_have_curator" in codes
    assert "country_proposal_published_countries_are_active" in codes
    assert "country_proposal_curators_are_editors" in codes
    contribution_issues = [
        issue
        for issue in report.issues
        if issue.entity_type == "country_proposal"
    ]
    assert contribution_issues == []


def test_published_or_review_proposal_missing_curator_is_critical(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_proposals_without_curator",
        lambda *_: [{"id": "p1", "slug": "wakanda"}],
    )

    issues: list[Any] = []
    checks: list[Any] = []
    _append_country_contribution_checks(CONNECTION, issues, checks)

    assert any(
        issue.code == "country_proposal_missing_curator" for issue in issues
    )
    failed = next(
        c for c in checks if c.code == "country_proposals_have_curator"
    )
    assert failed.status == "failed"


def test_published_proposal_with_inactive_country_is_critical(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_proposals_with_inactive_country",
        lambda *_: [{"id": "p1", "slug": "wakanda"}],
    )

    issues: list[Any] = []
    checks: list[Any] = []
    _append_country_contribution_checks(CONNECTION, issues, checks)

    assert any(
        issue.code == "country_proposal_published_country_inactive"
        for issue in issues
    )


def test_curator_with_non_editor_role_is_high_severity(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_proposals_with_non_editor_curator",
        lambda *_: [{"id": "p1", "slug": "wakanda", "curator_role": "user"}],
    )

    issues: list[Any] = []
    checks: list[Any] = []
    _append_country_contribution_checks(CONNECTION, issues, checks)

    matching = next(
        issue
        for issue in issues
        if issue.code == "country_proposal_curator_not_editor"
    )
    assert matching.severity == "high"
