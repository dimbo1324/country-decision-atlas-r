from app.repositories import data_quality as data_quality_repository
from app.services import data_quality
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_clean_auth_surface_produces_no_issues(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    report = data_quality.build_data_quality_report(CONNECTION)
    assert report.valid is True
    auth_codes = {
        i.code
        for i in report.issues
        if "user" in i.code
        or "session" in i.code
        or "telegram" in i.code
        or "watchlist" in i.code
    }
    assert auth_codes == set()


def test_missing_active_owner_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(data_quality_repository, "count_active_owners", lambda *_: 0)
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "missing_active_owner" for i in report.issues)
    assert any(
        i.severity == "critical"
        for i in report.issues
        if i.code == "missing_active_owner"
    )
    assert report.valid is False


def test_user_invalid_role_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_users_with_invalid_role",
        lambda *_: [{"id": "user-1", "role": "superadmin"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "user_invalid_role" for i in report.issues)
    assert report.valid is False


def test_user_invalid_status_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_users_with_invalid_status",
        lambda *_: [{"id": "user-1", "status": "banned"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "user_invalid_status" for i in report.issues)
    assert report.valid is False


def test_active_user_missing_password_credential_is_warning(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_active_users_missing_password_credential",
        lambda *_: [{"id": "user-1"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    matching = [
        i for i in report.issues if i.code == "active_user_missing_password_credential"
    ]
    assert matching
    assert all(i.severity == "warning" for i in matching)
    assert report.valid is True


def test_password_credential_invalid_hash_format_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_password_credentials_with_invalid_hash_format",
        lambda *_: [{"id": "cred-1", "password_hash": "plaintext"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(
        i.code == "password_credential_invalid_hash_format" for i in report.issues
    )
    assert report.valid is False


def test_suspended_user_with_active_session_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_suspended_or_deleted_users_with_active_sessions",
        lambda *_: [{"id": "session-1", "user_id": "user-1"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(
        i.code == "suspended_or_deleted_user_has_active_session" for i in report.issues
    )
    assert report.valid is False


def test_expired_session_not_revoked_is_warning(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_expired_sessions_not_revoked",
        lambda *_: [{"id": "session-1"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    matching = [i for i in report.issues if i.code == "expired_session_not_revoked"]
    assert matching
    assert all(i.severity == "warning" for i in matching)
    assert report.valid is True


def test_session_empty_token_hash_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_sessions_with_empty_token_hash",
        lambda *_: [{"id": "session-1"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "session_empty_token_hash" for i in report.issues)
    assert report.valid is False


def test_telegram_link_invalid_status_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_telegram_links_with_invalid_status",
        lambda *_: [{"id": "link-1", "status": "pending"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "telegram_link_invalid_status" for i in report.issues)
    assert report.valid is False


def test_telegram_link_missing_unlinked_at_is_warning(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_unlinked_telegram_links_missing_unlinked_at",
        lambda *_: [{"id": "link-1"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    matching = [
        i for i in report.issues if i.code == "telegram_link_missing_unlinked_at"
    ]
    assert matching
    assert all(i.severity == "warning" for i in matching)
    assert report.valid is True


def test_telegram_link_duplicate_active_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_duplicate_active_telegram_links",
        lambda *_: [{"telegram_user_id": "tg-1"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "telegram_link_duplicate_active" for i in report.issues)
    assert report.valid is False


def test_watchlist_references_missing_user_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_watchlists_referencing_missing_users",
        lambda *_: [{"id": "watchlist-1"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "watchlist_references_missing_user" for i in report.issues)
    assert report.valid is False


def test_watchlist_duplicate_active_entry_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_duplicate_active_watchlist_entries",
        lambda *_: [{"user_id": "user-1"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "watchlist_duplicate_active_entry" for i in report.issues)
    assert report.valid is False


def test_watchlist_archived_missing_archived_at_is_warning(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_archived_watchlists_missing_archived_at",
        lambda *_: [{"id": "watchlist-1"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    matching = [
        i for i in report.issues if i.code == "watchlist_archived_missing_archived_at"
    ]
    assert matching
    assert all(i.severity == "warning" for i in matching)
    assert report.valid is True


def test_watchlist_null_notification_flag_is_critical(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_watchlists_with_null_notification_flags",
        lambda *_: [{"id": "watchlist-1"}],
    )
    report = data_quality.build_data_quality_report(CONNECTION)
    assert any(i.code == "watchlist_null_notification_flag" for i in report.issues)
    assert report.valid is False
