from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_country_contribution_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_published_proposals_without_curator(connection):
        issues.append(
            _issue(
                "country_proposal_missing_curator",
                "critical",
                "country_proposal",
                row.get("id"),
                "Country proposal cannot be in review or published without an assigned curator.",
                row,
            )
        )
    checks.append(
        _check(
            "country_proposals_have_curator",
            issues,
            ["country_proposal_missing_curator"],
        )
    )

    for row in repository.list_published_proposals_with_inactive_country(
        connection
    ):
        issues.append(
            _issue(
                "country_proposal_published_country_inactive",
                "critical",
                "country_proposal",
                row.get("id"),
                "Published country proposal's country must be active.",
                row,
            )
        )
    checks.append(
        _check(
            "country_proposal_published_countries_are_active",
            issues,
            ["country_proposal_published_country_inactive"],
        )
    )

    for row in repository.list_proposals_with_non_editor_curator(connection):
        issues.append(
            _issue(
                "country_proposal_curator_not_editor",
                "high",
                "country_proposal",
                row.get("id"),
                "Country proposal curator must hold the editor, admin, or owner role.",
                row,
            )
        )
    checks.append(
        _check(
            "country_proposal_curators_are_editors",
            issues,
            ["country_proposal_curator_not_editor"],
        )
    )
