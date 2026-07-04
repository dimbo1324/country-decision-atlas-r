"""Data-quality checks for the Migration Board: broken public posts and interaction-rule violations."""

from app.repositories import data_quality as data_quality_repository
from app.services import data_quality
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_migration_board_data_quality_checks_are_registered(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)

    report = data_quality.build_data_quality_report(CONNECTION)
    check_codes = {check.code for check in report.checks}

    assert "migration_board_published_posts_are_approved" in check_codes
    assert (
        "migration_board_published_posts_have_acknowledgements" in check_codes
    )
    assert "migration_board_public_text_has_no_pii" in check_codes
    assert "migration_board_contact_requests_are_valid" in check_codes
    assert "migration_board_reports_are_valid" in check_codes
    assert "migration_board_blocks_are_valid" in check_codes


def test_migration_board_data_quality_detects_broken_public_post(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_migration_board_posts_without_approval",
        lambda *_: [{"id": "post-1", "moderation_status": "pending"}],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_migration_board_public_posts_with_pii",
        lambda *_: [
            {"id": "post-2", "title": "Contact me", "summary": "email"}
        ],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert {
        "migration_board_published_without_approval",
        "migration_board_public_text_contains_pii",
    }.issubset({issue.code for issue in report.issues})


def test_migration_board_data_quality_detects_interaction_violations(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_invalid_migration_board_contact_requests",
        lambda *_: [{"id": "request-1"}],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_invalid_migration_board_reports",
        lambda *_: [{"id": "report-1"}],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_invalid_migration_board_blocks",
        lambda *_: [{"id": "block-1"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert {
        "migration_board_contact_request_invalid",
        "migration_board_report_invalid",
        "migration_board_block_invalid",
    }.issubset({issue.code for issue in report.issues})
