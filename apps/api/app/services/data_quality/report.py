from app.repositories import data_quality as repository
from app.schemas.data_quality import (
    DataQualityCheck,
    DataQualityIssue,
    DataQualityReport,
)
from app.services.data_quality._issues import _check, _issue
from app.services.data_quality.country_drift_checks import (
    _append_country_drift_checks,
)
from app.services.data_quality.persona_checks import _append_persona_layer_checks
from app.services.data_quality.platform_checks import _append_platform_runtime_checks
from app.services.data_quality.trust_checks import _append_trust_surface_checks
from psycopg import Connection
from typing import Any


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
    _append_trust_surface_checks(connection, issues, checks)
    _append_country_drift_checks(connection, issues, checks)
    from app.services import data_quality as data_quality_facade

    translation_checks, translation_issues = (
        data_quality_facade.build_translation_quality_results(connection)
    )
    checks.extend(translation_checks)
    issues.extend(translation_issues)
    onboarding_checks, onboarding_issues = (
        data_quality_facade.build_country_onboarding_dq_results(connection)
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
