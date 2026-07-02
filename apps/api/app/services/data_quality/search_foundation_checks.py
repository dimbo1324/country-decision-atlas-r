from app.repositories import (
    data_quality as repository,
    search_index as search_index_repository,
)
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_search_foundation_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in search_index_repository.list_broken_search_documents(connection):
        issues.append(
            _issue(
                "search_document_invalid",
                "critical",
                "search_document",
                row.get("id"),
                "Search document is missing a required field (path, title, or content_hash).",
                row,
            )
        )
    checks.append(
        _check(
            "search_documents_valid",
            issues,
            ["search_document_invalid"],
        )
    )

    for row in repository.list_search_documents_referencing_non_published_content(
        connection
    ):
        issues.append(
            _issue(
                "search_document_references_non_published_content",
                "critical",
                "search_document",
                row.get("id"),
                "Search document is published but references non-published content.",
                row,
            )
        )
    checks.append(
        _check(
            "search_documents_reference_published_content",
            issues,
            ["search_document_references_non_published_content"],
        )
    )

    if search_index_repository.count_search_documents(connection) == 0:
        issues.append(
            _issue(
                "search_index_empty",
                "accepted_mvp_warning",
                "search_document",
                None,
                "Search index is empty because the rebuild script has not run yet.",
                {"classification": "future_scope"},
            )
        )
        return

    coverage_sources = (
        (
            "search_coverage_gap_country",
            repository.list_active_countries_missing_from_index,
        ),
        (
            "search_coverage_gap_route",
            repository.list_published_routes_missing_from_index,
        ),
        (
            "search_coverage_gap_legal_signal",
            repository.list_published_legal_signals_missing_from_index,
        ),
        (
            "search_coverage_gap_source",
            repository.list_published_sources_missing_from_index,
        ),
        (
            "search_coverage_gap_evidence_item",
            repository.list_published_evidence_missing_from_index,
        ),
    )
    for code, fetcher in coverage_sources:
        for row in fetcher(connection):
            issues.append(
                _issue(
                    code,
                    "critical",
                    "search_document",
                    row.get("id"),
                    "Published entity is missing from the search index.",
                    row,
                )
            )
        checks.append(_check(f"{code}_check", issues, [code]))

    for row in repository.list_search_documents_with_incomplete_locale_coverage(
        connection
    ):
        issues.append(
            _issue(
                "search_document_incomplete_locale_coverage",
                "warning",
                "search_document",
                row.get("entity_id"),
                "Published entity is indexed in fewer than both supported locales.",
                row,
            )
        )
    checks.append(
        _check(
            "search_documents_have_full_locale_coverage",
            issues,
            ["search_document_incomplete_locale_coverage"],
        )
    )
