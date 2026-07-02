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
