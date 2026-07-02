from app.repositories import data_quality as data_quality_repository
from app.services import data_quality
from psycopg import Connection
from tests.test_data_quality_validation import install_clean_report_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_ai_data_quality_checks_are_registered(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)

    report = data_quality.build_data_quality_report(CONNECTION)
    check_codes = {check.code for check in report.checks}

    assert "ai_feature_flags_exist" in check_codes
    assert "ai_feature_flags_have_public_access_rules" in check_codes
    assert "ai_logs_do_not_store_forbidden_metadata_keys" in check_codes


def test_ai_data_quality_detects_forbidden_log_metadata(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_ai_logs_with_forbidden_metadata_keys",
        lambda *_: [{"id": "log-1", "metadata": {"email": "hidden@example.com"}}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert any(issue.code == "ai_log_forbidden_metadata_key" for issue in report.issues)
