from app.repositories import data_quality as data_quality_repository
from app.repositories.data_quality import ai as ai_quality_repository
from app.services import data_quality
import inspect
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
    assert "ai_drafts_have_citations" in check_codes
    assert "ai_drafts_have_model_metadata" in check_codes
    assert "ai_draft_statuses_are_valid" in check_codes
    assert "contradiction_candidates_are_traceable" in check_codes
    assert "confirmed_contradictions_have_review_metadata" in check_codes
    assert "published_community_content_is_moderated" in check_codes
    assert "published_qna_answers_have_body" in check_codes
    assert "pending_data_error_reports_are_reviewed_timely" in check_codes
    assert "user_story_rating_scores_are_valid" in check_codes


def test_ai_data_quality_detects_forbidden_log_metadata(monkeypatch: Any) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_ai_logs_with_forbidden_metadata_keys",
        lambda *_: [{"id": "log-1", "metadata": {"email": "hidden@example.com"}}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert any(issue.code == "ai_log_forbidden_metadata_key" for issue in report.issues)


def test_contradiction_candidate_data_quality_sql_matches_schema() -> None:
    source = inspect.getsource(
        ai_quality_repository.list_contradiction_candidates_without_traceability
    )
    source += inspect.getsource(
        ai_quality_repository.list_confirmed_contradiction_candidates_without_review
    )

    assert "route_id" not in source
    assert "legal_signal_id" not in source
    assert "entity_id::text" in source


def test_ai_data_quality_detects_untraceable_draft_and_candidate(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_ai_drafts_without_citations",
        lambda *_: [{"id": "draft-1", "draft_type": "summary", "citations": []}],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_ai_drafts_missing_model_metadata",
        lambda *_: [{"id": "draft-2", "provider": None, "model_name": "fake"}],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_contradiction_candidates_without_traceability",
        lambda *_: [{"id": "candidate-1", "source_ids": [], "evidence_item_ids": []}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert {
        "ai_draft_citations_missing",
        "ai_draft_model_metadata_missing",
        "contradiction_candidate_traceability_missing",
    }.issubset({issue.code for issue in report.issues})


def test_ai_data_quality_detects_lifecycle_and_review_violations(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_ai_drafts_with_invalid_status",
        lambda *_: [{"id": "draft-1", "status": "published"}],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_confirmed_contradiction_candidates_without_review",
        lambda *_: [{"id": "candidate-1", "reviewed_at": None, "reviewed_by": None}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert {
        "ai_draft_status_invalid",
        "confirmed_contradiction_review_metadata_missing",
    }.issubset({issue.code for issue in report.issues})


def test_ai_data_quality_detects_unmoderated_published_community_content(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_community_questions_without_moderation",
        lambda *_: [{"id": "question-1", "status": "published"}],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_community_answers_without_moderation",
        lambda *_: [{"id": "answer-1", "status": "published"}],
    )
    monkeypatch.setattr(
        data_quality_repository,
        "list_published_qna_answers_without_body",
        lambda *_: [{"id": "answer-2", "body": ""}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert {
        "published_community_question_moderation_missing",
        "published_community_answer_moderation_missing",
        "published_qna_answer_body_missing",
    }.issubset({issue.code for issue in report.issues})


def test_ai_data_quality_keeps_stale_pending_report_as_warning(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_stale_pending_data_error_reports",
        lambda *_: [{"id": "report-1", "status": "pending"}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is True
    assert report.critical_issues_count == 0
    assert report.warnings_count == 1
    assert any(
        issue.code == "data_error_report_pending_stale" and issue.severity == "warning"
        for issue in report.issues
    )


def test_ai_data_quality_detects_invalid_user_story_rating_score(
    monkeypatch: Any,
) -> None:
    install_clean_report_fakes(monkeypatch)
    monkeypatch.setattr(
        data_quality_repository,
        "list_user_story_ratings_with_invalid_scores",
        lambda *_: [{"id": "rating-1", "official_expectation_score": 101}],
    )

    report = data_quality.build_data_quality_report(CONNECTION)

    assert report.valid is False
    assert any(
        issue.code == "user_story_rating_score_invalid" for issue in report.issues
    )
