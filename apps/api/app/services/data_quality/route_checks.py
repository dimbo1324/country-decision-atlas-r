from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_route_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_published_routes_without_sources(connection):
        issues.append(
            _issue(
                "published_route_missing_source",
                "critical",
                "route",
                row.get("id"),
                "Published route has no linked source.",
                row,
            )
        )
    checks.append(
        _check(
            "published_routes_have_sources", issues, ["published_route_missing_source"]
        )
    )
    for row in repository.list_published_routes_missing_required_text(connection):
        issues.append(
            _issue(
                "published_route_missing_required_text",
                "critical",
                "route",
                row.get("id"),
                "Published route is missing required text field.",
                row,
            )
        )
    checks.append(
        _check(
            "published_routes_have_required_text",
            issues,
            ["published_route_missing_required_text"],
        )
    )
    for row in repository.list_route_source_country_mismatches(connection):
        issues.append(
            _issue(
                "route_source_country_mismatch",
                "critical",
                "route",
                row.get("id"),
                "Route source belongs to a different country than the route.",
                row,
            )
        )
    checks.append(
        _check(
            "route_sources_match_route_country",
            issues,
            ["route_source_country_mismatch"],
        )
    )
    for row in repository.list_route_evidence_country_mismatches(connection):
        issues.append(
            _issue(
                "route_evidence_country_mismatch",
                "critical",
                "route",
                row.get("id"),
                "Route evidence belongs to a different country than the route.",
                row,
            )
        )
    checks.append(
        _check(
            "route_evidence_matches_route_country",
            issues,
            ["route_evidence_country_mismatch"],
        )
    )
    for row in repository.list_published_routes_missing_legal_status(connection):
        issues.append(
            _issue(
                "published_route_missing_legal_status",
                "critical",
                "route",
                row.get("id"),
                "Published route is missing legal_status.",
                row,
            )
        )
    checks.append(
        _check(
            "published_routes_have_legal_status",
            issues,
            ["published_route_missing_legal_status"],
        )
    )
    for row in repository.list_published_routes_with_all_eligibility_unknown(
        connection
    ):
        issues.append(
            _issue(
                "published_route_all_eligibility_unknown",
                "warning",
                "route",
                row.get("id"),
                "Published route has all eligibility flags set to unknown.",
                row,
            )
        )
    for row in repository.list_published_routes_without_documents(connection):
        issues.append(
            _issue(
                "published_route_missing_documents",
                "warning",
                "route",
                row.get("id"),
                "Published route has no linked documents.",
                row,
            )
        )
    for row in repository.list_published_routes_with_unknown_legal_status(connection):
        issues.append(
            _issue(
                "published_route_legal_status_unknown",
                "warning",
                "route",
                row.get("id"),
                "Published route has unknown legal_status.",
                row,
            )
        )
    checks.append(
        _check(
            "published_routes_quality",
            issues,
            [
                "published_route_all_eligibility_unknown",
                "published_route_missing_documents",
                "published_route_legal_status_unknown",
            ],
        )
    )
