from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_content_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_scores_without_breakdowns(connection):
        issues.append(
            _issue(
                "score_breakdown_missing",
                "critical",
                "country_score",
                row.get("country_score_id"),
                "Country score has no breakdown rows.",
                row,
            )
        )
    for row in repository.list_scores_with_incomplete_breakdowns(connection):
        issues.append(
            _issue(
                "score_breakdown_count_invalid",
                "critical",
                "country_score",
                row.get("country_score_id"),
                "Country score must have exactly 7 breakdown rows.",
                row,
            )
        )
    for row in repository.list_scores_with_invalid_weight_sum(connection):
        issues.append(
            _issue(
                "score_breakdown_weight_sum_invalid",
                "critical",
                "country_score",
                row.get("country_score_id"),
                "Country score breakdown weights must sum to expected total.",
                row,
            )
        )
    for row in repository.list_published_score_breakdowns_without_source_ids(
        connection
    ):
        issues.append(
            _issue(
                "score_breakdown_source_ids_missing",
                "critical",
                "country_score_breakdown",
                row.get("id"),
                "Country score breakdown must reference at least one source.",
                row,
            )
        )
    checks.append(
        _check(
            "mvp_score_breakdowns_complete",
            issues,
            [
                "score_breakdown_missing",
                "score_breakdown_count_invalid",
                "score_breakdown_weight_sum_invalid",
                "score_breakdown_source_ids_missing",
            ],
        )
    )
    for row in repository.list_published_legal_signals_without_source(
        connection
    ):
        issues.append(
            _issue(
                "published_legal_signal_source_missing",
                "critical",
                "legal_signal",
                row.get("id"),
                "Published legal signal has no source.",
                row,
            )
        )
    checks.append(
        _check(
            "published_legal_signals_have_sources",
            issues,
            ["published_legal_signal_source_missing"],
        )
    )
    for row in repository.list_published_legal_signals_without_evidence(
        connection
    ):
        issues.append(
            _issue(
                "published_legal_signal_evidence_missing",
                "warning",
                "legal_signal",
                row.get("id"),
                "Published legal signal has no evidence item.",
                row,
            )
        )
    checks.append(
        _check(
            "published_legal_signals_have_evidence",
            issues,
            ["published_legal_signal_evidence_missing"],
        )
    )
    for (
        row
    ) in repository.list_published_legal_signals_with_missing_legal_status(
        connection
    ):
        issues.append(
            _issue(
                "published_legal_signal_legal_status_missing",
                "critical",
                "legal_signal",
                row.get("id"),
                "Published legal signal is missing legal_status.",
                row,
            )
        )
    for (
        row
    ) in repository.list_published_legal_signals_with_unknown_legal_status(
        connection
    ):
        issues.append(
            _issue(
                "published_legal_signal_legal_status_unknown",
                "warning",
                "legal_signal",
                row.get("id"),
                "Published legal signal still has unknown legal_status.",
                row,
            )
        )
    checks.append(
        _check(
            "legal_signals_published_have_legal_status",
            issues,
            [
                "published_legal_signal_legal_status_missing",
                "published_legal_signal_legal_status_unknown",
            ],
        )
    )
    for row in repository.list_evidence_without_source(connection):
        issues.append(
            _issue(
                "evidence_source_missing",
                "critical",
                "evidence_item",
                row.get("id"),
                "Evidence item has no source.",
                row,
            )
        )
    for row in repository.list_evidence_without_country(connection):
        issues.append(
            _issue(
                "evidence_country_missing",
                "critical",
                "evidence_item",
                row.get("id"),
                "Evidence item has no country.",
                row,
            )
        )
    checks.append(
        _check(
            "evidence_is_traceable",
            issues,
            ["evidence_source_missing", "evidence_country_missing"],
        )
    )
    for row in repository.list_published_sources_with_missing_required_fields(
        connection
    ):
        issues.append(
            _issue(
                "published_source_required_field_missing",
                "critical",
                "source",
                row.get("id"),
                "Published source is missing required field.",
                row,
            )
        )
    checks.append(
        _check(
            "published_sources_have_required_fields",
            issues,
            ["published_source_required_field_missing"],
        )
    )
    for row in repository.list_published_sources_with_example_invalid_url(
        connection
    ):
        issues.append(
            _issue(
                "published_source_example_invalid_url",
                "critical",
                "source",
                row.get("id"),
                "Published source must not use example.invalid URLs.",
                row,
            )
        )
    checks.append(
        _check(
            "published_sources_use_real_urls",
            issues,
            ["published_source_example_invalid_url"],
        )
    )
    for row in repository.list_invalid_synthetic_user_stories(connection):
        issues.append(
            _issue(
                "synthetic_user_story_invalid",
                "critical",
                "user_story",
                row.get("id"),
                "Synthetic user story must not look like a verified real story.",
                row,
            )
        )
    checks.append(
        _check(
            "synthetic_user_stories_are_marked",
            issues,
            ["synthetic_user_story_invalid"],
        )
    )
    for row in repository.list_country_cards_with_empty_major_sections(
        connection
    ):
        issues.append(
            _issue(
                "country_card_section_missing",
                "critical",
                "country_card",
                row.get("id"),
                "Published country card has empty major public sections.",
                row,
            )
        )
    for row in repository.list_country_cards_with_demo_source_summary(
        connection
    ):
        issues.append(
            _issue(
                "country_card_source_summary_demo",
                "critical",
                "country_card",
                row.get("id"),
                "Published country card source summary must describe real sources.",
                row,
            )
        )
    checks.append(
        _check(
            "country_cards_have_public_sections",
            issues,
            [
                "country_card_section_missing",
                "country_card_source_summary_demo",
            ],
        )
    )
