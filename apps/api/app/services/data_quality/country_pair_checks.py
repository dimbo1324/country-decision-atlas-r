from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_country_pair_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_published_pairs_without_sources(connection):
        issues.append(
            _issue(
                "country_pair_missing_source",
                "critical",
                "country_pair_compatibility",
                row.get("id"),
                "Published country pair compatibility has no linked source.",
                row,
            )
        )
    checks.append(
        _check(
            "country_pairs_have_sources",
            issues,
            ["country_pair_missing_source"],
        )
    )

    for row in repository.list_published_pairs_missing_last_verified_at(connection):
        issues.append(
            _issue(
                "country_pair_missing_last_verified_at",
                "critical",
                "country_pair_compatibility",
                row.get("id"),
                "Published country pair compatibility is missing last_verified_at.",
                row,
            )
        )
    checks.append(
        _check(
            "country_pairs_have_last_verified_at",
            issues,
            ["country_pair_missing_last_verified_at"],
        )
    )

    for row in repository.list_stale_published_pairs(connection):
        issues.append(
            _issue(
                "country_pair_stale",
                "warning",
                "country_pair_compatibility",
                row.get("id"),
                "Published country pair compatibility freshness_status is stale.",
                row,
            )
        )
    checks.append(
        _check(
            "country_pairs_not_stale",
            issues,
            ["country_pair_stale"],
        )
    )
