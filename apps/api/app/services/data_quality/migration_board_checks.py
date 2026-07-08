from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_migration_board_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_published_migration_board_posts_without_approval(
        connection
    ):
        issues.append(
            _issue(
                "migration_board_published_without_approval",
                "critical",
                "migration_board_post",
                row.get("id"),
                "Published migration board post must be approved by moderation.",
                row,
            )
        )
    checks.append(
        _check(
            "migration_board_published_posts_are_approved",
            issues,
            ["migration_board_published_without_approval"],
        )
    )

    for row in repository.list_published_migration_board_posts_without_acknowledgements(
        connection
    ):
        issues.append(
            _issue(
                "migration_board_published_without_acknowledgements",
                "critical",
                "migration_board_post",
                row.get("id"),
                "Published migration board post must include risk and legal acknowledgements.",
                row,
            )
        )
    checks.append(
        _check(
            "migration_board_published_posts_have_acknowledgements",
            issues,
            ["migration_board_published_without_acknowledgements"],
        )
    )

    for (
        row
    ) in repository.list_migration_board_posts_with_route_country_mismatch(
        connection
    ):
        issues.append(
            _issue(
                "migration_board_route_country_mismatch",
                "critical",
                "migration_board_post",
                row.get("id"),
                "Migration board post route must belong to destination country.",
                row,
            )
        )
    checks.append(
        _check(
            "migration_board_routes_match_destination_country",
            issues,
            ["migration_board_route_country_mismatch"],
        )
    )

    for row in repository.list_migration_board_public_posts_with_pii(
        connection
    ):
        issues.append(
            _issue(
                "migration_board_public_text_contains_pii",
                "critical",
                "migration_board_post",
                row.get("id"),
                "Public migration board title or summary contains direct contact details.",
                {"id": row.get("id")},
            )
        )
    checks.append(
        _check(
            "migration_board_public_text_has_no_pii",
            issues,
            ["migration_board_public_text_contains_pii"],
        )
    )

    for row in repository.list_invalid_migration_board_contact_requests(
        connection
    ):
        issues.append(
            _issue(
                "migration_board_contact_request_invalid",
                "critical",
                "migration_board_contact_request",
                row.get("id"),
                "Migration board contact request violates status, post, self-contact, or block rules.",
                row,
            )
        )
    for (
        row
    ) in repository.list_duplicate_pending_migration_board_contact_requests(
        connection
    ):
        issues.append(
            _issue(
                "migration_board_contact_request_duplicate_pending",
                "critical",
                "migration_board_contact_request",
                row.get("post_id"),
                "Migration board post has duplicate pending contact requests from the same user.",
                row,
            )
        )
    checks.append(
        _check(
            "migration_board_contact_requests_are_valid",
            issues,
            [
                "migration_board_contact_request_invalid",
                "migration_board_contact_request_duplicate_pending",
            ],
        )
    )

    for row in repository.list_invalid_migration_board_reports(connection):
        issues.append(
            _issue(
                "migration_board_report_invalid",
                "critical",
                "migration_board_report",
                row.get("id"),
                "Migration board report violates target, status, reason, or review metadata rules.",
                row,
            )
        )
    checks.append(
        _check(
            "migration_board_reports_are_valid",
            issues,
            ["migration_board_report_invalid"],
        )
    )

    for row in repository.list_invalid_migration_board_blocks(connection):
        issues.append(
            _issue(
                "migration_board_block_invalid",
                "critical",
                "migration_board_block",
                row.get("id"),
                "Migration board block must not target the blocker.",
                row,
            )
        )
    checks.append(
        _check(
            "migration_board_blocks_are_valid",
            issues,
            ["migration_board_block_invalid"],
        )
    )

    for row in repository.list_open_threads_without_active_contact(connection):
        issues.append(
            _issue(
                "migration_board_thread_open_without_active_contact",
                "critical",
                "contact_thread",
                row.get("id"),
                "Open community thread must have an accepted contact request.",
                row,
            )
        )
    checks.append(
        _check(
            "migration_board_threads_match_contact_status",
            issues,
            ["migration_board_thread_open_without_active_contact"],
        )
    )

    for row in repository.list_thread_messages_after_thread_closed(connection):
        issues.append(
            _issue(
                "migration_board_thread_message_after_closed",
                "critical",
                "thread_message",
                row.get("id"),
                "Thread message was created after its thread was closed.",
                row,
            )
        )
    for row in repository.list_thread_messages_after_block(connection):
        issues.append(
            _issue(
                "migration_board_thread_message_after_block",
                "critical",
                "thread_message",
                row.get("id"),
                "Thread message was created after the counterpart was blocked.",
                row,
            )
        )
    checks.append(
        _check(
            "migration_board_thread_messages_respect_closed_at",
            issues,
            [
                "migration_board_thread_message_after_closed",
                "migration_board_thread_message_after_block",
            ],
        )
    )
