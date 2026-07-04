from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_cii_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
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
    checks.append(
        _check("mvp_countries_have_cii", issues, ["cii_score_missing"])
    )
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
            "cii_scores_have_formula_metadata",
            issues,
            ["cii_formula_metadata_missing"],
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
    checks.append(
        _check("cii_weights_sum_to_one", issues, ["cii_weight_sum_invalid"])
    )
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
            "mvp_scenarios_have_cii_weights",
            issues,
            ["cii_scenario_weight_missing"],
        )
    )
    for row in repository.list_cii_scenario_weights_with_negative_values(
        connection
    ):
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
    for row in repository.list_cii_scenario_scores_missing_formula_metadata(
        connection
    ):
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
            "mvp_countries_have_all_cii_metrics",
            issues,
            ["cii_metric_value_missing"],
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
    for row in repository.list_cii_scores_with_non_geometric_aggregation(
        connection
    ):
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
    for row in repository.list_cii_metric_definitions_without_polarity(
        connection
    ):
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
