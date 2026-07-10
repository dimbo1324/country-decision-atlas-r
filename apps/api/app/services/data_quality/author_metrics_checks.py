from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from app.services.pii_patterns import contains_pii
from psycopg import Connection
from typing import Any


def _append_author_metrics_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_published_author_metrics_without_methodology(
        connection
    ):
        issues.append(
            _issue(
                "author_metric_published_without_methodology",
                "critical",
                "author_metric_definition",
                row.get("id"),
                "Published author metric must include a methodology description in both languages.",
                row,
            )
        )
    checks.append(
        _check(
            "author_metrics_published_have_methodology",
            issues,
            ["author_metric_published_without_methodology"],
        )
    )

    for (
        row
    ) in repository.list_author_metric_values_missing_source_or_experience(
        connection
    ):
        issues.append(
            _issue(
                "author_metric_value_missing_source_or_experience",
                "critical",
                "author_metric_value",
                row.get("id"),
                "Author metric value must have a source URL or be flagged as personal experience.",
                row,
            )
        )
    checks.append(
        _check(
            "author_metric_values_have_source_or_experience",
            issues,
            ["author_metric_value_missing_source_or_experience"],
        )
    )

    for row in repository.list_author_metric_values_out_of_scale(connection):
        issues.append(
            _issue(
                "author_metric_value_out_of_scale",
                "critical",
                "author_metric_value",
                row.get("id"),
                "Author metric value falls outside the definition's declared scale.",
                row,
            )
        )
    checks.append(
        _check(
            "author_metric_values_within_scale",
            issues,
            ["author_metric_value_out_of_scale"],
        )
    )

    for row in repository.list_published_public_author_metrics_text(connection):
        if contains_pii(
            str(row.get("name_en") or ""),
            str(row.get("name_ru") or ""),
            str(row.get("methodology_en") or ""),
            str(row.get("methodology_ru") or ""),
        ):
            issues.append(
                _issue(
                    "author_metric_public_text_contains_pii",
                    "critical",
                    "author_metric_definition",
                    row.get("id"),
                    "Published public author metric text contains direct contact details.",
                    {"id": row.get("id")},
                )
            )
    checks.append(
        _check(
            "author_metrics_public_text_has_no_pii",
            issues,
            ["author_metric_public_text_contains_pii"],
        )
    )

    for row in repository.list_author_metrics_with_dangling_fork_lineage(
        connection
    ):
        issues.append(
            _issue(
                "author_metric_dangling_fork_lineage",
                "critical",
                "author_metric_definition",
                row.get("id"),
                "Author metric fork references a source definition that no longer exists.",
                row,
            )
        )
    checks.append(
        _check(
            "author_metric_fork_lineage_is_valid",
            issues,
            ["author_metric_dangling_fork_lineage"],
        )
    )
