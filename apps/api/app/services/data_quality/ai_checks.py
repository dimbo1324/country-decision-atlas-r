from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_ai_foundation_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_missing_ai_feature_flags(connection):
        issues.append(
            _issue(
                "ai_feature_flag_missing",
                "critical",
                "feature_flag",
                row.get("feature_key"),
                "Required AI feature flag is missing.",
                row,
            )
        )
    checks.append(
        _check(
            "ai_feature_flags_exist",
            issues,
            ["ai_feature_flag_missing"],
        )
    )
    for row in repository.list_ai_feature_flags_without_public_access_rules(connection):
        issues.append(
            _issue(
                "ai_feature_flag_public_access_rule_missing",
                "critical",
                "feature_flag",
                row.get("feature_key"),
                "AI feature flag has no public access rule.",
                row,
            )
        )
    checks.append(
        _check(
            "ai_feature_flags_have_public_access_rules",
            issues,
            ["ai_feature_flag_public_access_rule_missing"],
        )
    )
    for row in repository.list_ai_logs_with_forbidden_metadata_keys(connection):
        issues.append(
            _issue(
                "ai_log_forbidden_metadata_key",
                "critical",
                "ai_interaction_log",
                row.get("id"),
                "AI interaction log metadata contains a forbidden key.",
                row,
            )
        )
    checks.append(
        _check(
            "ai_logs_do_not_store_forbidden_metadata_keys",
            issues,
            ["ai_log_forbidden_metadata_key"],
        )
    )
    for row in repository.list_ai_drafts_without_citations(connection):
        issues.append(
            _issue(
                "ai_draft_citations_missing",
                "critical",
                "ai_draft",
                row.get("id"),
                "AI draft must keep source citations before review or approval.",
                row,
            )
        )
    checks.append(
        _check(
            "ai_drafts_have_citations",
            issues,
            ["ai_draft_citations_missing"],
        )
    )
    for row in repository.list_ai_drafts_missing_model_metadata(connection):
        issues.append(
            _issue(
                "ai_draft_model_metadata_missing",
                "critical",
                "ai_draft",
                row.get("id"),
                "AI draft must record provider and model metadata.",
                row,
            )
        )
    checks.append(
        _check(
            "ai_drafts_have_model_metadata",
            issues,
            ["ai_draft_model_metadata_missing"],
        )
    )
    for row in repository.list_ai_drafts_with_invalid_status(connection):
        issues.append(
            _issue(
                "ai_draft_status_invalid",
                "critical",
                "ai_draft",
                row.get("id"),
                "AI draft has a status outside the approved lifecycle.",
                row,
            )
        )
    checks.append(
        _check(
            "ai_draft_statuses_are_valid",
            issues,
            ["ai_draft_status_invalid"],
        )
    )
    for row in repository.list_ai_drafts_with_invalid_draft_type(connection):
        issues.append(
            _issue(
                "ai_draft_type_invalid",
                "critical",
                "ai_draft",
                row.get("id"),
                "AI draft has a type outside the approved draft taxonomy.",
                row,
            )
        )
    checks.append(
        _check(
            "ai_draft_types_are_valid",
            issues,
            ["ai_draft_type_invalid"],
        )
    )
    for row in repository.list_approved_ai_drafts_without_review(connection):
        issues.append(
            _issue(
                "approved_ai_draft_review_metadata_missing",
                "critical",
                "ai_draft",
                row.get("id"),
                "Approved AI draft must include explicit review metadata.",
                row,
            )
        )
    checks.append(
        _check(
            "approved_ai_drafts_have_review_metadata",
            issues,
            ["approved_ai_draft_review_metadata_missing"],
        )
    )
    for row in repository.list_contradiction_candidates_without_traceability(
        connection
    ):
        issues.append(
            _issue(
                "contradiction_candidate_traceability_missing",
                "critical",
                "contradiction_candidate",
                row.get("id"),
                "Contradiction candidate must reference source or evidence records.",
                row,
            )
        )
    checks.append(
        _check(
            "contradiction_candidates_are_traceable",
            issues,
            ["contradiction_candidate_traceability_missing"],
        )
    )
    for row in repository.list_confirmed_contradiction_candidates_without_review(
        connection
    ):
        issues.append(
            _issue(
                "confirmed_contradiction_review_metadata_missing",
                "critical",
                "contradiction_candidate",
                row.get("id"),
                "Confirmed contradiction candidate must include review metadata.",
                row,
            )
        )
    checks.append(
        _check(
            "confirmed_contradictions_have_review_metadata",
            issues,
            ["confirmed_contradiction_review_metadata_missing"],
        )
    )
    published_community_moderation_issue_codes = [
        "published_community_question_moderation_missing",
        "published_community_answer_moderation_missing",
    ]
    for row in repository.list_published_community_questions_without_moderation(
        connection
    ):
        issues.append(
            _issue(
                "published_community_question_moderation_missing",
                "critical",
                "qna_question",
                row.get("id"),
                "Published community question must include moderation metadata.",
                row,
            )
        )
    for row in repository.list_published_community_answers_without_moderation(
        connection
    ):
        issues.append(
            _issue(
                "published_community_answer_moderation_missing",
                "critical",
                "qna_answer",
                row.get("id"),
                "Published community answer must include moderation metadata.",
                row,
            )
        )
    checks.append(
        _check(
            "published_community_content_is_moderated",
            issues,
            published_community_moderation_issue_codes,
        )
    )
    for row in repository.list_published_qna_questions_without_content(connection):
        issues.append(
            _issue(
                "published_qna_question_content_missing",
                "critical",
                "qna_question",
                row.get("id"),
                "Published Q&A question must have title and body text.",
                row,
            )
        )
    checks.append(
        _check(
            "published_qna_questions_have_content",
            issues,
            ["published_qna_question_content_missing"],
        )
    )
    for row in repository.list_published_qna_answers_without_body(connection):
        issues.append(
            _issue(
                "published_qna_answer_body_missing",
                "critical",
                "qna_answer",
                row.get("id"),
                "Published Q&A answer must have body text.",
                row,
            )
        )
    checks.append(
        _check(
            "published_qna_answers_have_body",
            issues,
            ["published_qna_answer_body_missing"],
        )
    )
    for row in repository.list_published_qna_answers_with_invalid_traceability_refs(
        connection
    ):
        issues.append(
            _issue(
                "published_qna_answer_traceability_refs_invalid",
                "critical",
                "qna_answer",
                row.get("id"),
                "Published Q&A answer traceability refs must be arrays.",
                row,
            )
        )
    checks.append(
        _check(
            "published_qna_answer_traceability_refs_are_valid",
            issues,
            ["published_qna_answer_traceability_refs_invalid"],
        )
    )
    for row in repository.list_qna_votes_with_invalid_type(connection):
        issues.append(
            _issue(
                "qna_vote_type_invalid",
                "critical",
                "qna_vote",
                row.get("id"),
                "Q&A vote type must stay within the approved taxonomy.",
                row,
            )
        )
    checks.append(
        _check(
            "qna_vote_types_are_valid",
            issues,
            ["qna_vote_type_invalid"],
        )
    )
    for row in repository.list_duplicate_qna_votes(connection):
        issues.append(
            _issue(
                "qna_vote_duplicate",
                "critical",
                "qna_vote",
                row.get("answer_id"),
                "Q&A answer has duplicate votes for the same identity and vote type.",
                row,
            )
        )
    checks.append(
        _check(
            "qna_votes_are_unique_per_identity",
            issues,
            ["qna_vote_duplicate"],
        )
    )
    for row in repository.list_stale_pending_data_error_reports(connection):
        issues.append(
            _issue(
                "data_error_report_pending_stale",
                "warning",
                "data_error_report",
                row.get("id"),
                "Pending data error report has not been reviewed for over 30 days.",
                row,
            )
        )
    checks.append(
        _check(
            "pending_data_error_reports_are_reviewed_timely",
            issues,
            ["data_error_report_pending_stale"],
        )
    )
    for row in repository.list_published_user_story_ratings_without_moderation(
        connection
    ):
        issues.append(
            _issue(
                "published_user_story_rating_moderation_missing",
                "critical",
                "user_story_rating",
                row.get("id"),
                "Published user story rating must include review metadata.",
                row,
            )
        )
    checks.append(
        _check(
            "published_user_story_ratings_are_moderated",
            issues,
            ["published_user_story_rating_moderation_missing"],
        )
    )
    for row in repository.list_user_story_ratings_with_invalid_scores(connection):
        issues.append(
            _issue(
                "user_story_rating_score_invalid",
                "critical",
                "user_story_rating",
                row.get("id"),
                "User story rating scores must stay within the 0-100 range.",
                row,
            )
        )
    checks.append(
        _check(
            "user_story_rating_scores_are_valid",
            issues,
            ["user_story_rating_score_invalid"],
        )
    )
