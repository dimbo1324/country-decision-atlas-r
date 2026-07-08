"""Data-quality checks for community threads: contact-status drift and post-close/block leaks."""

from app.repositories import data_quality as data_quality_repository
from app.services import data_quality
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_community_thread_data_quality_checks_are_registered(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)

    report = data_quality.build_data_quality_report(CONNECTION)
    check_codes = {check.code for check in report.checks}

    assert "migration_board_threads_match_contact_status" in check_codes
    assert "migration_board_thread_messages_respect_closed_at" in check_codes


def test_community_thread_data_quality_detects_open_thread_without_accepted_contact(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_open_threads_without_active_contact",
        lambda *_: [
            {
                "id": "thread-1",
                "status": "open",
                "contact_request_status": "cancelled",
            }
        ],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert "migration_board_thread_open_without_active_contact" in {
        issue.code for issue in report.issues
    }


def test_community_thread_data_quality_detects_message_after_close(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_thread_messages_after_thread_closed",
        lambda *_: [{"id": "message-1", "thread_id": "thread-1"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert "migration_board_thread_message_after_closed" in {
        issue.code for issue in report.issues
    }


def test_community_thread_data_quality_detects_message_after_block(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_thread_messages_after_block",
        lambda *_: [{"id": "message-2", "thread_id": "thread-2"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert "migration_board_thread_message_after_block" in {
        issue.code for issue in report.issues
    }
