from app.core.errors import api_error
from app.repositories import data_quality as repository
from app.schemas.data_quality import (
    DataQualityCheck,
    DataQualityIssue,
    DataQualityReport,
)
from app.services import persona_weights
from app.services.country_onboarding import build_country_onboarding_dq_results
from app.services.translation_quality import build_translation_quality_results
from fastapi import HTTPException
from psycopg import Connection
from typing import Any


COUNTRY_CARD_FIELDS = [
    "executive_summary",
    "migration_overview",
    "tax_overview",
    "cost_of_living_overview",
    "business_overview",
    "safety_overview",
    "legal_signals_summary",
    "risk_summary",
    "source_summary",
]


def build_data_quality_report(connection: Connection[Any]) -> DataQualityReport:
    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    for row in repository.list_missing_mvp_countries(connection):
        issues.append(
            _issue(
                "mvp_country_missing",
                "critical",
                "country",
                None,
                "Required MVP country is missing or inactive.",
                row,
            )
        )
    checks.append(_check("mvp_countries_exist", issues, ["mvp_country_missing"]))
    for row in repository.list_published_countries_without_cards(connection):
        issues.append(
            _issue(
                "country_card_missing",
                "critical",
                "country",
                row.get("id"),
                "Published MVP country has no published EN country card.",
                row,
            )
        )
    checks.append(_check("mvp_countries_have_cards", issues, ["country_card_missing"]))
    for row in repository.list_published_countries_without_sources(connection):
        issues.append(
            _issue(
                "country_sources_missing",
                "critical",
                "country",
                row.get("id"),
                "Published MVP country has no published sources.",
                row,
            )
        )
    checks.append(
        _check("mvp_countries_have_sources", issues, ["country_sources_missing"])
    )
    for row in repository.list_mvp_countries_with_too_few_published_sources(connection):
        issues.append(
            _issue(
                "mvp_country_published_source_count_low",
                "accepted_mvp_warning",
                "country",
                row.get("id"),
                "Published MVP country is below the future source-depth target.",
                {**row, "classification": "future_scope"},
            )
        )
    for row in repository.list_mvp_countries_with_too_few_published_evidence(
        connection
    ):
        issues.append(
            _issue(
                "mvp_country_published_evidence_count_low",
                "accepted_mvp_warning",
                "country",
                row.get("id"),
                "Published MVP country is below the future evidence-depth target.",
                {**row, "classification": "future_scope"},
            )
        )
    for row in repository.list_mvp_countries_with_too_few_published_legal_signals(
        connection
    ):
        issues.append(
            _issue(
                "mvp_country_published_legal_signal_count_low",
                "accepted_mvp_warning",
                "country",
                row.get("id"),
                "Published MVP country is below the future legal-signal depth target.",
                {**row, "classification": "future_scope"},
            )
        )
    checks.append(
        _check(
            "mvp_country_content_depth",
            issues,
            [
                "mvp_country_published_source_count_low",
                "mvp_country_published_evidence_count_low",
                "mvp_country_published_legal_signal_count_low",
            ],
        )
    )
    for row in repository.list_missing_country_scores_for_required_scenarios(
        connection
    ):
        issues.append(
            _issue(
                "country_score_missing",
                "critical",
                "country_score",
                None,
                "Country score is missing for required MVP scenario.",
                row,
            )
        )
    checks.append(
        _check("mvp_country_scores_complete", issues, ["country_score_missing"])
    )
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
    for row in repository.list_published_legal_signals_without_source(connection):
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
    for row in repository.list_published_legal_signals_without_evidence(connection):
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
    for row in repository.list_published_legal_signals_without_timeline_event(
        connection
    ):
        issues.append(
            _issue(
                "published_legal_signal_timeline_event_missing",
                "critical",
                "legal_signal",
                row.get("id"),
                "Published legal signal has no timeline event.",
                row,
            )
        )
    checks.append(
        _check(
            "published_legal_signals_have_timeline_events",
            issues,
            ["published_legal_signal_timeline_event_missing"],
        )
    )
    for row in repository.list_published_legal_signals_with_missing_legal_status(
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
    for row in repository.list_published_legal_signals_with_unknown_legal_status(
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
    for row in repository.list_review_sources_with_missing_required_fields(connection):
        issues.append(
            _issue(
                "review_source_required_field_missing",
                "critical",
                "source",
                row.get("id"),
                "Review source is missing a publish-required field.",
                row,
            )
        )
    for row in repository.list_review_evidence_items_with_missing_required_fields(
        connection
    ):
        issues.append(
            _issue(
                "review_evidence_required_field_missing",
                "critical",
                "evidence_item",
                row.get("id"),
                "Review evidence item is missing a publish-required field.",
                row,
            )
        )
    for row in repository.list_review_legal_signals_with_missing_required_fields(
        connection
    ):
        issues.append(
            _issue(
                "review_legal_signal_required_field_missing",
                "critical",
                "legal_signal",
                row.get("id"),
                "Review legal signal is missing a publish-required field.",
                row,
            )
        )
    checks.append(
        _check(
            "review_content_has_required_fields",
            issues,
            [
                "review_source_required_field_missing",
                "review_evidence_required_field_missing",
                "review_legal_signal_required_field_missing",
            ],
        )
    )
    for row in repository.list_published_evidence_items_with_missing_required_fields(
        connection
    ):
        issues.append(
            _issue(
                "published_evidence_validation_failed",
                "critical",
                "evidence_item",
                row.get("id"),
                "Published evidence item no longer passes publication validation.",
                row,
            )
        )
    for row in repository.list_published_legal_signals_with_missing_required_fields(
        connection
    ):
        issues.append(
            _issue(
                "published_legal_signal_validation_failed",
                "critical",
                "legal_signal",
                row.get("id"),
                "Published legal signal no longer passes publication validation.",
                row,
            )
        )
    checks.append(
        _check(
            "published_content_passes_validation",
            issues,
            [
                "published_source_required_field_missing",
                "published_evidence_validation_failed",
                "published_legal_signal_validation_failed",
            ],
        )
    )
    for row in repository.list_invalid_domain_events_for_dq(connection):
        issues.append(
            _issue(
                "domain_event_invalid",
                "critical",
                "domain_event",
                row.get("id"),
                "Domain event is inconsistent with relay readiness rules.",
                row,
            )
        )
    checks.append(
        _check(
            "domain_events_consistent",
            issues,
            ["domain_event_invalid"],
        )
    )
    checks.append(
        DataQualityCheck(
            code="domain_events_no_historical_notification_storm",
            status="passed",
        )
    )
    timeline_checks = [
        (
            repository.list_timeline_events_with_invalid_date,
            "timeline_event_date_invalid",
            "critical",
            "Timeline event must have an event date.",
        ),
        (
            repository.list_timeline_events_with_invalid_impact_direction,
            "timeline_event_impact_direction_invalid",
            "critical",
            "Timeline event has an invalid impact direction.",
        ),
        (
            repository.list_timeline_events_with_invalid_impact_level,
            "timeline_event_impact_level_invalid",
            "critical",
            "Timeline event has an invalid impact level.",
        ),
        (
            repository.list_timeline_events_with_country_mismatch,
            "timeline_event_country_mismatch",
            "critical",
            "Timeline event country differs from its legal signal country.",
        ),
        (
            repository.list_timeline_events_without_traceability,
            "timeline_event_traceability_missing",
            "warning",
            "Timeline event has neither source nor evidence.",
        ),
        (
            repository.list_unplanned_future_timeline_events,
            "timeline_event_future_date",
            "critical",
            "Timeline event date is in the future.",
        ),
    ]
    timeline_codes: list[str] = []
    for query, code, severity, message in timeline_checks:
        timeline_codes.append(code)
        for row in query(connection):
            issues.append(
                _issue(
                    code,
                    severity,
                    "legal_signal_event",
                    row.get("id"),
                    message,
                    row,
                )
            )
    checks.append(_check("legal_signal_timeline_is_valid", issues, timeline_codes))
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
    for row in repository.list_published_sources_with_example_invalid_url(connection):
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
    for row in repository.list_country_cards_with_empty_major_sections(connection):
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
    for row in repository.list_country_cards_with_demo_source_summary(connection):
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
            ["country_card_section_missing", "country_card_source_summary_demo"],
        )
    )
    for row in repository.list_mvp_countries_missing_cii(connection):
        issues.append(
            _issue(
                "cii_score_missing",
                "critical",
                "country",
                None,
                "MVP country has no CII score for version v1.0.",
                row,
            )
        )
    checks.append(_check("mvp_countries_have_cii", issues, ["cii_score_missing"]))
    for row in repository.list_cii_scores_missing_formula_metadata(connection):
        issues.append(
            _issue(
                "cii_formula_metadata_missing",
                "critical",
                "country",
                None,
                "CII score is missing formula_version or aggregation_method.",
                row,
            )
        )
    checks.append(
        _check(
            "cii_scores_have_formula_metadata", issues, ["cii_formula_metadata_missing"]
        )
    )
    for row in repository.list_cii_metric_weights_with_invalid_sum(connection):
        issues.append(
            _issue(
                "cii_weight_sum_invalid",
                "critical",
                "scenario_metric_weights",
                None,
                "CII metric weights do not sum to approximately 1.0.",
                row,
            )
        )
    checks.append(_check("cii_weights_sum_to_one", issues, ["cii_weight_sum_invalid"]))
    for row in repository.list_mvp_scenarios_missing_cii_weights(connection):
        issues.append(
            _issue(
                "cii_scenario_weight_missing",
                "critical",
                "scenario_metric_weights",
                None,
                "MVP scenario is missing CII weight for an active metric.",
                row,
            )
        )
    checks.append(
        _check(
            "mvp_scenarios_have_cii_weights", issues, ["cii_scenario_weight_missing"]
        )
    )
    for row in repository.list_cii_scenario_weights_with_negative_values(connection):
        issues.append(
            _issue(
                "cii_scenario_weight_negative",
                "critical",
                "scenario_metric_weights",
                None,
                "CII scenario metric weight is negative.",
                row,
            )
        )
    checks.append(
        _check(
            "cii_scenario_weights_non_negative",
            issues,
            ["cii_scenario_weight_negative"],
        )
    )
    for row in repository.list_cii_scenario_weights_exceeding_one(connection):
        issues.append(
            _issue(
                "cii_scenario_weight_exceeds_one",
                "critical",
                "scenario_metric_weights",
                None,
                "CII scenario metric weight exceeds 1.",
                row,
            )
        )
    checks.append(
        _check(
            "cii_scenario_weights_not_exceeding_one",
            issues,
            ["cii_scenario_weight_exceeds_one"],
        )
    )
    for row in repository.list_mvp_scenarios_missing_cii_scores(connection):
        issues.append(
            _issue(
                "cii_scenario_score_missing",
                "critical",
                "country_cii_scores",
                None,
                "MVP country has no CII score for a required scenario.",
                row,
            )
        )
    checks.append(
        _check(
            "mvp_countries_have_scenario_cii_scores",
            issues,
            ["cii_scenario_score_missing"],
        )
    )
    for row in repository.list_cii_scenario_scores_missing_formula_metadata(connection):
        issues.append(
            _issue(
                "cii_scenario_formula_metadata_missing",
                "critical",
                "country_cii_scores",
                None,
                "Scenario-specific CII score is missing formula_version or aggregation_method.",
                row,
            )
        )
    checks.append(
        _check(
            "cii_scenario_scores_have_formula_metadata",
            issues,
            ["cii_scenario_formula_metadata_missing"],
        )
    )
    for row in repository.list_mvp_metrics_missing_values(connection):
        issues.append(
            _issue(
                "cii_metric_value_missing",
                "critical",
                "country",
                None,
                "MVP country is missing a value for an active CII metric.",
                row,
            )
        )
    checks.append(
        _check(
            "mvp_countries_have_all_cii_metrics", issues, ["cii_metric_value_missing"]
        )
    )
    for row in repository.list_cii_scores_out_of_range(connection):
        issues.append(
            _issue(
                "cii_score_out_of_range",
                "critical",
                "country",
                None,
                "CII overall_score is outside the valid 0-100 range.",
                row,
            )
        )
    checks.append(
        _check("cii_scores_in_valid_range", issues, ["cii_score_out_of_range"])
    )
    for row in repository.list_inactive_mvp_scenarios(connection):
        issues.append(
            _issue(
                "mvp_scenario_inactive",
                "critical",
                "scenario",
                None,
                "Required MVP scenario is missing or inactive.",
                row,
            )
        )
    checks.append(_check("mvp_scenarios_active", issues, ["mvp_scenario_inactive"]))
    for row in repository.list_cii_scores_with_non_geometric_aggregation(connection):
        issues.append(
            _issue(
                "cii_aggregation_method_not_geometric",
                "critical",
                "country_cii_scores",
                None,
                "CII scenario score does not use geometric aggregation.",
                row,
            )
        )
    checks.append(
        _check(
            "cii_scores_use_geometric_aggregation",
            issues,
            ["cii_aggregation_method_not_geometric"],
        )
    )
    for row in repository.list_cii_metric_definitions_without_polarity(connection):
        issues.append(
            _issue(
                "cii_metric_polarity_missing",
                "critical",
                "cii_metric_definitions",
                None,
                "Active CII metric definition is missing polarity.",
                row,
            )
        )
    checks.append(
        _check(
            "cii_metric_definitions_have_polarity",
            issues,
            ["cii_metric_polarity_missing"],
        )
    )
    for row in repository.list_mvp_countries_without_legal_events(connection):
        issues.append(
            _issue(
                "legal_timeline_no_events_for_country",
                "critical",
                "country",
                None,
                "MVP country has no legal signal timeline events.",
                row,
            )
        )
    checks.append(
        _check(
            "legal_timeline_has_events_per_country",
            issues,
            ["legal_timeline_no_events_for_country"],
        )
    )
    for row in repository.list_published_routes_without_sources(connection):
        issues.append(
            _issue(
                "published_route_missing_source",
                "critical",
                "route",
                row.get("id"),
                "Published route has no linked source.",
                row,
            )
        )
    checks.append(
        _check(
            "published_routes_have_sources", issues, ["published_route_missing_source"]
        )
    )
    for row in repository.list_published_routes_missing_required_text(connection):
        issues.append(
            _issue(
                "published_route_missing_required_text",
                "critical",
                "route",
                row.get("id"),
                "Published route is missing required text field.",
                row,
            )
        )
    checks.append(
        _check(
            "published_routes_have_required_text",
            issues,
            ["published_route_missing_required_text"],
        )
    )
    for row in repository.list_route_source_country_mismatches(connection):
        issues.append(
            _issue(
                "route_source_country_mismatch",
                "critical",
                "route",
                row.get("id"),
                "Route source belongs to a different country than the route.",
                row,
            )
        )
    checks.append(
        _check(
            "route_sources_match_route_country",
            issues,
            ["route_source_country_mismatch"],
        )
    )
    for row in repository.list_route_evidence_country_mismatches(connection):
        issues.append(
            _issue(
                "route_evidence_country_mismatch",
                "critical",
                "route",
                row.get("id"),
                "Route evidence belongs to a different country than the route.",
                row,
            )
        )
    checks.append(
        _check(
            "route_evidence_matches_route_country",
            issues,
            ["route_evidence_country_mismatch"],
        )
    )
    for row in repository.list_published_routes_missing_legal_status(connection):
        issues.append(
            _issue(
                "published_route_missing_legal_status",
                "critical",
                "route",
                row.get("id"),
                "Published route is missing legal_status.",
                row,
            )
        )
    checks.append(
        _check(
            "published_routes_have_legal_status",
            issues,
            ["published_route_missing_legal_status"],
        )
    )
    for row in repository.list_published_routes_with_all_eligibility_unknown(
        connection
    ):
        issues.append(
            _issue(
                "published_route_all_eligibility_unknown",
                "warning",
                "route",
                row.get("id"),
                "Published route has all eligibility flags set to unknown.",
                row,
            )
        )
    for row in repository.list_published_routes_without_documents(connection):
        issues.append(
            _issue(
                "published_route_missing_documents",
                "warning",
                "route",
                row.get("id"),
                "Published route has no linked documents.",
                row,
            )
        )
    for row in repository.list_published_routes_with_unknown_legal_status(connection):
        issues.append(
            _issue(
                "published_route_legal_status_unknown",
                "warning",
                "route",
                row.get("id"),
                "Published route has unknown legal_status.",
                row,
            )
        )
    checks.append(
        _check(
            "published_routes_quality",
            issues,
            [
                "published_route_all_eligibility_unknown",
                "published_route_missing_documents",
                "published_route_legal_status_unknown",
            ],
        )
    )
    _append_persona_layer_checks(connection, issues, checks)
    _append_platform_runtime_checks(connection, issues, checks)
    translation_checks, translation_issues = build_translation_quality_results(
        connection
    )
    checks.extend(translation_checks)
    issues.extend(translation_issues)
    onboarding_checks, onboarding_issues = build_country_onboarding_dq_results(
        connection
    )
    checks.extend(onboarding_checks)
    issues.extend(onboarding_issues)
    critical_issues_count = sum(1 for issue in issues if issue.severity == "critical")
    warnings_count = sum(
        1 for issue in issues if issue.severity in {"warning", "accepted_mvp_warning"}
    )
    return DataQualityReport(
        overall_status="valid" if critical_issues_count == 0 else "invalid",
        valid=critical_issues_count == 0,
        critical_issues_count=critical_issues_count,
        warnings_count=warnings_count,
        checks=checks,
        issues=issues,
    )


def _append_persona_layer_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_active_personas_missing_required_fields(connection):
        issues.append(
            _issue(
                "persona_required_fields",
                "critical",
                "persona",
                row.get("persona_slug"),
                "Active persona is missing a required field.",
                row,
            )
        )
    checks.append(
        _check("persona_required_fields", issues, ["persona_required_fields"])
    )

    for row in repository.list_active_personas_missing_metric_modifiers(connection):
        issues.append(
            _issue(
                "persona_modifier_coverage",
                "critical",
                "persona",
                row.get("persona_slug"),
                "Active persona is missing a CII metric modifier.",
                row,
            )
        )
    checks.append(
        _check("persona_modifier_coverage", issues, ["persona_modifier_coverage"])
    )

    for row in repository.list_persona_modifiers_out_of_range(connection):
        issues.append(
            _issue(
                "persona_modifier_range",
                "critical",
                "persona",
                row.get("persona_slug"),
                "Persona modifier is outside the allowed range.",
                {**row, "expected_range": [-0.5, 0.5]},
            )
        )
    checks.append(_check("persona_modifier_range", issues, ["persona_modifier_range"]))

    _append_persona_adjusted_weight_issues(connection, issues)
    checks.append(
        _check(
            "persona_adjusted_weights_valid",
            issues,
            ["persona_adjusted_weights_valid"],
        )
    )

    for row in repository.list_active_personas_missing_descriptions(connection):
        issues.append(
            _issue(
                "persona_descriptions",
                "warning",
                "persona",
                row.get("persona_slug"),
                "Active persona is missing optional description content.",
                row,
            )
        )
    checks.append(_check("persona_descriptions", issues, ["persona_descriptions"]))

    for row in repository.list_inactive_personas_with_modifiers(connection):
        issues.append(
            _issue(
                "inactive_persona_modifiers",
                "warning",
                "persona",
                row.get("persona_slug"),
                "Inactive persona still has metric modifiers.",
                row,
            )
        )
    checks.append(
        _check("inactive_persona_modifiers", issues, ["inactive_persona_modifiers"])
    )


def _append_platform_runtime_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_enabled_feature_flags_without_access_rules(connection):
        issues.append(
            _issue(
                "enabled_feature_flag_without_access_rule",
                "critical",
                "feature_flag",
                row.get("key"),
                "Enabled feature flag has no access rule.",
                row,
            )
        )
    checks.append(
        _check(
            "enabled_feature_flags_have_access_rules",
            issues,
            ["enabled_feature_flag_without_access_rule"],
        )
    )
    for row in repository.list_disabled_feature_flags_without_access_rules(connection):
        issues.append(
            _issue(
                "disabled_feature_flag_without_access_rule",
                "warning",
                "feature_flag",
                row.get("key"),
                "Disabled feature flag has no access rule.",
                row,
            )
        )
    checks.append(
        _check(
            "feature_flags_have_valid_access_rules",
            issues,
            ["disabled_feature_flag_without_access_rule"],
        )
    )
    for row in repository.list_data_journal_events_with_internal_payload_fields(
        connection
    ):
        issues.append(
            _issue(
                "data_journal_internal_payload_field",
                "critical",
                "domain_event",
                row.get("id"),
                "Data journal source event contains internal payload fields.",
                row,
            )
        )
    checks.append(
        _check(
            "data_journal_does_not_expose_internal_fields",
            issues,
            ["data_journal_internal_payload_field"],
        )
    )
    for row in repository.list_data_journal_events_referencing_non_public_content(
        connection
    ):
        issues.append(
            _issue(
                "data_journal_non_public_reference",
                "critical",
                "domain_event",
                row.get("id"),
                "Data journal source event references non-public content.",
                row,
            )
        )
    checks.append(
        _check(
            "data_journal_entries_reference_public_content",
            issues,
            ["data_journal_non_public_reference"],
        )
    )
    checks.append(_check("cache_config_is_safe", issues, []))


def _append_persona_adjusted_weight_issues(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
) -> None:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in repository.list_persona_adjusted_weight_inputs(connection):
        key = (str(row["persona_slug"]), str(row["scenario_slug"]))
        grouped.setdefault(key, []).append(row)

    for (persona_slug, scenario_slug), rows in grouped.items():
        try:
            adjusted = persona_weights.build_adjusted_weights(rows)
        except HTTPException as exc:
            error_code = "persona_adjusted_weights_invalid"
            if isinstance(exc.detail, dict):
                error_code = str(exc.detail.get("error", {}).get("code", error_code))
            issues.append(
                _issue(
                    "persona_adjusted_weights_valid",
                    "critical",
                    "persona",
                    persona_slug,
                    "Persona adjusted weights could not be built.",
                    {
                        "persona_slug": persona_slug,
                        "scenario_slug": scenario_slug,
                        "error_code": error_code,
                    },
                )
            )
            continue
        weight_sum = sum(float(row["adjusted_weight"]) for row in adjusted)
        negative = [
            row["metric_slug"] for row in adjusted if float(row["adjusted_weight"]) < 0
        ]
        if negative or abs(weight_sum - 1.0) > 0.000001:
            issues.append(
                _issue(
                    "persona_adjusted_weights_valid",
                    "critical",
                    "persona",
                    persona_slug,
                    "Persona adjusted weights are invalid.",
                    {
                        "persona_slug": persona_slug,
                        "scenario_slug": scenario_slug,
                        "error_code": "persona_adjusted_weights_invalid",
                        "weight_sum": weight_sum,
                        "negative_metric_slugs": negative,
                    },
                )
            )


def validate_source_for_publish(source: dict[str, Any]) -> list[DataQualityIssue]:
    issues = _required_field_issues(
        source,
        "source",
        ["title", "url", "publisher", "source_type"],
        "source_required_field_missing",
        "Published source is missing required field.",
    )
    if _missing(source.get("confidence")) and _missing(source.get("reliability_level")):
        issues.append(
            _issue(
                "source_confidence_missing",
                "critical",
                "source",
                source.get("id"),
                "Published source is missing confidence/reliability level.",
                {"field": "confidence"},
            )
        )
    return issues


def validate_legal_signal_for_publish(
    legal_signal: dict[str, Any],
) -> list[DataQualityIssue]:
    issues = _required_field_issues(
        legal_signal,
        "legal_signal",
        [
            "country_id",
            "source_id",
            "signal_type",
            "impact_direction",
            "impact_level",
        ],
        "legal_signal_required_field_missing",
        "Published legal signal is missing required field.",
    )
    if _missing(legal_signal.get("title_en")) and _missing(legal_signal.get("title")):
        issues.append(_missing_field_issue(legal_signal, "legal_signal", "title_en"))
    if _missing(legal_signal.get("summary_en")) and _missing(
        legal_signal.get("summary")
    ):
        issues.append(_missing_field_issue(legal_signal, "legal_signal", "summary_en"))
    if _missing(legal_signal.get("confidence")) and _missing(
        legal_signal.get("confidence_level")
    ):
        issues.append(_missing_field_issue(legal_signal, "legal_signal", "confidence"))
    return issues


def validate_evidence_item_for_publish(
    evidence_item: dict[str, Any],
) -> list[DataQualityIssue]:
    issues = _required_field_issues(
        evidence_item,
        "evidence_item",
        ["source_id", "country_id"],
        "evidence_required_field_missing",
        "Published evidence item is missing required field.",
    )
    if _missing(evidence_item.get("claim")) and _missing(evidence_item.get("title")):
        issues.append(_missing_field_issue(evidence_item, "evidence_item", "claim"))
    if _missing(evidence_item.get("confidence")) and _missing(
        evidence_item.get("confidence_level")
    ):
        issues.append(
            _missing_field_issue(evidence_item, "evidence_item", "confidence")
        )
    if (
        _missing(evidence_item.get("url"))
        and _missing(evidence_item.get("excerpt"))
        and _missing(evidence_item.get("quote"))
    ):
        issues.append(_missing_field_issue(evidence_item, "evidence_item", "excerpt"))
    return issues


def validate_country_card_for_publish(
    country_card: dict[str, Any],
) -> list[DataQualityIssue]:
    if any(not _missing(country_card.get(field)) for field in COUNTRY_CARD_FIELDS):
        return []
    return [
        _issue(
            "country_card_public_text_missing",
            "critical",
            "country_card",
            country_card.get("id"),
            "Country card cannot be published because public text is empty.",
            {"fields": COUNTRY_CARD_FIELDS},
        )
    ]


def validate_user_story_for_publish(
    user_story: dict[str, Any],
) -> list[DataQualityIssue]:
    issues = _required_field_issues(
        user_story,
        "user_story",
        ["origin_country_id", "destination_country_id", "scenario", "year"],
        "user_story_required_field_missing",
        "Published user story is missing required field.",
    )
    if user_story.get("verification_status") == "verified":
        issues.append(
            _issue(
                "user_story_verified_without_verification",
                "critical",
                "user_story",
                user_story.get("id"),
                "User story cannot be marked verified without verification workflow.",
                {"verification_status": user_story.get("verification_status")},
            )
        )
    if user_story.get("is_synthetic"):
        notes = str(user_story.get("notes") or "").lower()
        if user_story.get("verification_status") != "synthetic" or not (
            "synthetic" in notes or "demo" in notes
        ):
            issues.append(
                _issue(
                    "synthetic_user_story_invalid",
                    "critical",
                    "user_story",
                    user_story.get("id"),
                    "Synthetic user story must not look like a verified real story.",
                    {
                        "verification_status": user_story.get("verification_status"),
                        "notes": user_story.get("notes"),
                    },
                )
            )
    return issues


def raise_if_critical_issues(issues: list[DataQualityIssue]) -> None:
    critical_issues = [issue for issue in issues if issue.severity == "critical"]
    if critical_issues:
        raise api_error(
            422,
            "data_quality_validation_failed",
            "Content cannot be published because data quality checks failed.",
            {"issues": [issue.model_dump(mode="json") for issue in critical_issues]},
        )


def _required_field_issues(
    data: dict[str, Any],
    entity_type: str,
    fields: list[str],
    code: str,
    message: str,
) -> list[DataQualityIssue]:
    return [
        _issue(
            code,
            "critical",
            entity_type,
            data.get("id"),
            message,
            {"field": field},
        )
        for field in fields
        if _missing(data.get(field))
    ]


def _missing_field_issue(
    data: dict[str, Any], entity_type: str, field: str
) -> DataQualityIssue:
    return _issue(
        f"{entity_type}_required_field_missing",
        "critical",
        entity_type,
        data.get("id"),
        f"Published {entity_type} is missing required field.",
        {"field": field},
    )


def _issue(
    code: str,
    severity: str,
    entity_type: str,
    entity_id: Any,
    message: str,
    details: dict[str, Any],
) -> DataQualityIssue:
    return DataQualityIssue(
        code=code,
        severity=severity,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        message=message,
        details={str(key): value for key, value in details.items()},
    )


def _missing(value: Any) -> bool:
    return value is None or value == ""


def _check(
    code: str, issues: list[DataQualityIssue], issue_codes: list[str]
) -> DataQualityCheck:
    failed = any(issue.code in issue_codes for issue in issues)
    return DataQualityCheck(code=code, status="failed" if failed else "passed")
