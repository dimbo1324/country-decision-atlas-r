from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_users_and_sessions_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    if repository.count_active_owners(connection) == 0:
        issues.append(
            _issue(
                "missing_active_owner",
                "critical",
                "user",
                None,
                "No active owner user exists.",
                {},
            )
        )
    checks.append(_check("at_least_one_active_owner", issues, ["missing_active_owner"]))

    for row in repository.list_users_with_invalid_role(connection):
        issues.append(
            _issue(
                "user_invalid_role",
                "critical",
                "user",
                row.get("id"),
                "User has an invalid role value.",
                row,
            )
        )
    checks.append(_check("users_have_valid_roles", issues, ["user_invalid_role"]))

    for row in repository.list_users_with_invalid_status(connection):
        issues.append(
            _issue(
                "user_invalid_status",
                "critical",
                "user",
                row.get("id"),
                "User has an invalid status value.",
                row,
            )
        )
    checks.append(_check("users_have_valid_statuses", issues, ["user_invalid_status"]))

    for row in repository.list_active_users_missing_password_credential(connection):
        issues.append(
            _issue(
                "active_user_missing_password_credential",
                "warning",
                "user",
                row.get("id"),
                "Active user has no password credential configured.",
                row,
            )
        )
    checks.append(
        _check(
            "active_users_have_password_credential",
            issues,
            ["active_user_missing_password_credential"],
        )
    )

    for row in repository.list_password_credentials_with_invalid_hash_format(
        connection
    ):
        issues.append(
            _issue(
                "password_credential_invalid_hash_format",
                "critical",
                "user_auth_credential",
                row.get("id"),
                "Password credential hash does not match the expected format.",
                row,
            )
        )
    checks.append(
        _check(
            "password_credentials_have_valid_hash_format",
            issues,
            ["password_credential_invalid_hash_format"],
        )
    )

    for row in repository.list_suspended_or_deleted_users_with_active_sessions(
        connection
    ):
        issues.append(
            _issue(
                "suspended_or_deleted_user_has_active_session",
                "critical",
                "auth_session",
                row.get("id"),
                "Suspended or deleted user has an active session.",
                row,
            )
        )
    checks.append(
        _check(
            "suspended_and_deleted_users_have_no_active_sessions",
            issues,
            ["suspended_or_deleted_user_has_active_session"],
        )
    )

    for row in repository.list_expired_sessions_not_revoked(connection):
        issues.append(
            _issue(
                "expired_session_not_revoked",
                "warning",
                "auth_session",
                row.get("id"),
                "Session has expired but was not marked as revoked.",
                row,
            )
        )
    checks.append(
        _check(
            "expired_sessions_are_cleaned_up",
            issues,
            ["expired_session_not_revoked"],
        )
    )

    for row in repository.list_sessions_with_empty_token_hash(connection):
        issues.append(
            _issue(
                "session_empty_token_hash",
                "critical",
                "auth_session",
                row.get("id"),
                "Session is missing a token hash.",
                row,
            )
        )
    checks.append(
        _check(
            "sessions_have_token_hash",
            issues,
            ["session_empty_token_hash"],
        )
    )


def _append_telegram_link_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_telegram_links_with_invalid_status(connection):
        issues.append(
            _issue(
                "telegram_link_invalid_status",
                "critical",
                "user_telegram_link",
                row.get("id"),
                "Telegram link has an invalid status value.",
                row,
            )
        )
    checks.append(
        _check(
            "telegram_links_have_valid_status",
            issues,
            ["telegram_link_invalid_status"],
        )
    )

    for row in repository.list_linked_telegram_links_missing_linked_at(connection):
        issues.append(
            _issue(
                "telegram_link_missing_linked_at",
                "critical",
                "user_telegram_link",
                row.get("id"),
                "Linked Telegram identity is missing linked_at.",
                row,
            )
        )
    checks.append(
        _check(
            "linked_telegram_links_have_linked_at",
            issues,
            ["telegram_link_missing_linked_at"],
        )
    )

    for row in repository.list_unlinked_telegram_links_missing_unlinked_at(connection):
        issues.append(
            _issue(
                "telegram_link_missing_unlinked_at",
                "warning",
                "user_telegram_link",
                row.get("id"),
                "Unlinked Telegram identity is missing unlinked_at.",
                row,
            )
        )
    checks.append(
        _check(
            "unlinked_telegram_links_have_unlinked_at",
            issues,
            ["telegram_link_missing_unlinked_at"],
        )
    )

    for row in repository.list_telegram_links_referencing_missing_users(connection):
        issues.append(
            _issue(
                "telegram_link_references_missing_user",
                "critical",
                "user_telegram_link",
                row.get("id"),
                "Telegram link references a user that no longer exists.",
                row,
            )
        )
    checks.append(
        _check(
            "telegram_links_reference_existing_users",
            issues,
            ["telegram_link_references_missing_user"],
        )
    )

    for row in repository.list_duplicate_active_telegram_links(connection):
        issues.append(
            _issue(
                "telegram_link_duplicate_active",
                "critical",
                "user_telegram_link",
                row.get("telegram_user_id"),
                "Telegram user id is linked to more than one active web user.",
                row,
            )
        )
    checks.append(
        _check(
            "telegram_links_unique_per_telegram_user",
            issues,
            ["telegram_link_duplicate_active"],
        )
    )


def _append_watchlist_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_watchlists_referencing_missing_users(connection):
        issues.append(
            _issue(
                "watchlist_references_missing_user",
                "critical",
                "watchlist",
                row.get("id"),
                "Watchlist entry references a user that no longer exists.",
                row,
            )
        )
    checks.append(
        _check(
            "watchlists_reference_existing_users",
            issues,
            ["watchlist_references_missing_user"],
        )
    )

    for row in repository.list_watchlists_referencing_missing_countries(connection):
        issues.append(
            _issue(
                "watchlist_references_missing_country",
                "critical",
                "watchlist",
                row.get("id"),
                "Watchlist entry references a country that no longer exists.",
                row,
            )
        )
    checks.append(
        _check(
            "watchlists_reference_existing_countries",
            issues,
            ["watchlist_references_missing_country"],
        )
    )

    for row in repository.list_watchlists_with_invalid_status(connection):
        issues.append(
            _issue(
                "watchlist_invalid_status",
                "critical",
                "watchlist",
                row.get("id"),
                "Watchlist entry has an invalid status value.",
                row,
            )
        )
    checks.append(
        _check("watchlists_have_valid_status", issues, ["watchlist_invalid_status"])
    )

    for row in repository.list_duplicate_active_watchlist_entries(connection):
        issues.append(
            _issue(
                "watchlist_duplicate_active_entry",
                "critical",
                "watchlist",
                row.get("user_id"),
                "User has more than one active watchlist entry for the same country.",
                row,
            )
        )
    checks.append(
        _check(
            "watchlists_no_duplicate_active_entries",
            issues,
            ["watchlist_duplicate_active_entry"],
        )
    )

    for row in repository.list_archived_watchlists_missing_archived_at(connection):
        issues.append(
            _issue(
                "watchlist_archived_missing_archived_at",
                "warning",
                "watchlist",
                row.get("id"),
                "Archived watchlist entry is missing archived_at.",
                row,
            )
        )
    checks.append(
        _check(
            "archived_watchlists_have_archived_at",
            issues,
            ["watchlist_archived_missing_archived_at"],
        )
    )

    for row in repository.list_watchlists_with_null_notification_flags(connection):
        issues.append(
            _issue(
                "watchlist_null_notification_flag",
                "critical",
                "watchlist",
                row.get("id"),
                "Watchlist entry has a null notification preference.",
                row,
            )
        )
    checks.append(
        _check(
            "watchlists_have_notification_flags_set",
            issues,
            ["watchlist_null_notification_flag"],
        )
    )


def _append_auth_watchlist_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    _append_users_and_sessions_checks(connection, issues, checks)
    _append_telegram_link_checks(connection, issues, checks)
    _append_watchlist_checks(connection, issues, checks)
