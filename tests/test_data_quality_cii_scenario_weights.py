from typing import Any
from unittest.mock import MagicMock, patch


_REPO = "app.repositories.data_quality"
_SVC = "app.services.data_quality"

MVP_SCENARIOS = [
    "relocation_residence",
    "permanent_residence_citizenship",
    "low_budget_living",
    "business_self_employment",
    "safety_political_risk",
]


def _make_connection() -> MagicMock:
    return MagicMock()


def _run_report_with_patches(**overrides: Any) -> Any:
    from app.services.data_quality import build_data_quality_report

    empty: list[Any] = []
    defaults = {
        "list_missing_mvp_countries": empty,
        "list_published_countries_without_cards": empty,
        "list_published_countries_without_sources": empty,
        "list_mvp_countries_with_too_few_published_sources": empty,
        "list_mvp_countries_with_too_few_published_evidence": empty,
        "list_mvp_countries_with_too_few_published_legal_signals": empty,
        "list_missing_country_scores_for_required_scenarios": empty,
        "list_scores_without_breakdowns": empty,
        "list_scores_with_incomplete_breakdowns": empty,
        "list_scores_with_invalid_weight_sum": empty,
        "list_published_score_breakdowns_without_source_ids": empty,
        "list_published_legal_signals_without_source": empty,
        "list_published_legal_signals_without_evidence": empty,
        "list_evidence_without_source": empty,
        "list_evidence_without_country": empty,
        "list_published_sources_with_missing_required_fields": empty,
        "list_published_sources_with_example_invalid_url": empty,
        "list_invalid_synthetic_user_stories": empty,
        "list_country_cards_with_empty_major_sections": empty,
        "list_country_cards_with_demo_source_summary": empty,
        "list_mvp_countries_missing_cii": empty,
        "list_cii_scores_missing_formula_metadata": empty,
        "list_cii_metric_weights_with_invalid_sum": empty,
        "list_mvp_metrics_missing_values": empty,
        "list_cii_scores_out_of_range": empty,
        "list_mvp_scenarios_missing_cii_weights": empty,
        "list_cii_scenario_weights_with_negative_values": empty,
        "list_cii_scenario_weights_exceeding_one": empty,
        "list_mvp_scenarios_missing_cii_scores": empty,
        "list_cii_scenario_scores_missing_formula_metadata": empty,
        "list_inactive_mvp_scenarios": empty,
        "list_cii_scores_with_non_geometric_aggregation": empty,
        "list_cii_metric_definitions_without_polarity": empty,
        "list_mvp_countries_without_legal_events": empty,
        "list_published_legal_signals_without_timeline_event": empty,
        "list_timeline_events_with_invalid_date": empty,
        "list_timeline_events_with_invalid_impact_direction": empty,
        "list_timeline_events_with_invalid_impact_level": empty,
        "list_timeline_events_with_country_mismatch": empty,
        "list_timeline_events_without_traceability": empty,
        "list_unplanned_future_timeline_events": empty,
    }
    defaults.update(overrides)

    patches = {f"{_REPO}.{fn}": MagicMock(return_value=v) for fn, v in defaults.items()}

    translation_patch = patch(
        f"{_SVC}.build_translation_quality_results",
        return_value=([], []),
    )

    with (
        translation_patch,
        patch.multiple(_REPO, **{k.split(".")[-1]: v for k, v in patches.items()}),
    ):
        return build_data_quality_report(_make_connection())


class TestDataQualityScenarioWeightChecks:
    def test_missing_scenario_weight_produces_critical_issue(self) -> None:
        missing = [{"scenario_slug": "relocation_residence", "metric_slug": "safety"}]
        report = _run_report_with_patches(
            list_mvp_scenarios_missing_cii_weights=missing
        )
        codes = {i.code for i in report.issues}
        assert "cii_scenario_weight_missing" in codes
        assert report.valid is False

    def test_check_mvp_scenarios_have_cii_weights_passes_when_empty(self) -> None:
        report = _run_report_with_patches()
        check_codes = {c.code for c in report.checks}
        assert "mvp_scenarios_have_cii_weights" in check_codes
        passing = {c.code for c in report.checks if c.status == "passed"}
        assert "mvp_scenarios_have_cii_weights" in passing

    def test_negative_weight_produces_critical_issue(self) -> None:
        negative = [
            {
                "scenario_slug": "business_self_employment",
                "metric_slug": "safety",
                "weight": -0.1,
            }
        ]
        report = _run_report_with_patches(
            list_cii_scenario_weights_with_negative_values=negative
        )
        codes = {i.code for i in report.issues}
        assert "cii_scenario_weight_negative" in codes
        assert report.valid is False

    def test_negative_weight_check_passes_when_empty(self) -> None:
        report = _run_report_with_patches()
        passing = {c.code for c in report.checks if c.status == "passed"}
        assert "cii_scenario_weights_non_negative" in passing

    def test_weight_exceeding_one_produces_critical_issue(self) -> None:
        over = [
            {
                "scenario_slug": "relocation_residence",
                "metric_slug": "safety",
                "weight": 1.1,
            }
        ]
        report = _run_report_with_patches(list_cii_scenario_weights_exceeding_one=over)
        codes = {i.code for i in report.issues}
        assert "cii_scenario_weight_exceeds_one" in codes
        assert report.valid is False

    def test_weight_exceeding_one_check_passes_when_empty(self) -> None:
        report = _run_report_with_patches()
        passing = {c.code for c in report.checks if c.status == "passed"}
        assert "cii_scenario_weights_not_exceeding_one" in passing

    def test_invalid_weight_sum_produces_critical_issue(self) -> None:
        bad_sum = [
            {"version": "v1.0", "scenario_slug": "low_budget_living", "weight_sum": 0.9}
        ]
        report = _run_report_with_patches(
            list_cii_metric_weights_with_invalid_sum=bad_sum
        )
        codes = {i.code for i in report.issues}
        assert "cii_weight_sum_invalid" in codes
        assert report.valid is False

    def test_missing_scenario_cii_score_produces_critical_issue(self) -> None:
        missing = [{"country_slug": "russia", "scenario_slug": "safety_political_risk"}]
        report = _run_report_with_patches(list_mvp_scenarios_missing_cii_scores=missing)
        codes = {i.code for i in report.issues}
        assert "cii_scenario_score_missing" in codes
        assert report.valid is False

    def test_mvp_countries_have_scenario_cii_scores_check_exists(self) -> None:
        report = _run_report_with_patches()
        check_codes = {c.code for c in report.checks}
        assert "mvp_countries_have_scenario_cii_scores" in check_codes

    def test_scenario_formula_metadata_missing_produces_critical_issue(self) -> None:
        missing_meta = [
            {
                "country_slug": "uruguay",
                "version": "v1.0",
                "scenario_slug": "business_self_employment",
                "formula_version": None,
                "aggregation_method": "geometric",
            }
        ]
        report = _run_report_with_patches(
            list_cii_scenario_scores_missing_formula_metadata=missing_meta
        )
        codes = {i.code for i in report.issues}
        assert "cii_scenario_formula_metadata_missing" in codes
        assert report.valid is False

    def test_scenario_formula_metadata_check_passes_when_all_present(self) -> None:
        report = _run_report_with_patches()
        passing = {c.code for c in report.checks if c.status == "passed"}
        assert "cii_scenario_scores_have_formula_metadata" in passing

    def test_all_scenario_weight_checks_present_in_report(self) -> None:
        report = _run_report_with_patches()
        check_codes = {c.code for c in report.checks}
        expected_checks = {
            "mvp_scenarios_have_cii_weights",
            "cii_scenario_weights_non_negative",
            "cii_scenario_weights_not_exceeding_one",
            "mvp_countries_have_scenario_cii_scores",
            "cii_scenario_scores_have_formula_metadata",
        }
        assert expected_checks.issubset(check_codes)
