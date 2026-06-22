from typing import Any
from unittest.mock import MagicMock, patch


_REPO = "app.repositories.data_quality"
_SVC = "app.services.data_quality"


def _make_connection() -> MagicMock:
    return MagicMock()


def _run_report(**overrides: Any) -> Any:
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
        "list_published_legal_signals_without_timeline_event": empty,
        "list_timeline_events_with_invalid_date": empty,
        "list_timeline_events_with_invalid_impact_direction": empty,
        "list_timeline_events_with_invalid_impact_level": empty,
        "list_timeline_events_with_country_mismatch": empty,
        "list_timeline_events_without_traceability": empty,
        "list_unplanned_future_timeline_events": empty,
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
    }
    defaults.update(overrides)
    patches = {f"{_REPO}.{fn}": MagicMock(return_value=v) for fn, v in defaults.items()}
    translation_patch = patch(
        f"{_SVC}.build_translation_quality_results", return_value=([], [])
    )
    with (
        translation_patch,
        patch.multiple(_REPO, **{k.split(".")[-1]: v for k, v in patches.items()}),
    ):
        return build_data_quality_report(_make_connection())


class TestCompareMatrixGuardrails:
    def test_inactive_mvp_scenario_produces_critical_issue(self) -> None:
        inactive = [{"scenario_slug": "relocation_residence"}]
        report = _run_report(list_inactive_mvp_scenarios=inactive)
        codes = {i.code for i in report.issues}
        assert "mvp_scenario_inactive" in codes
        assert report.valid is False

    def test_mvp_scenarios_active_check_passes_when_all_active(self) -> None:
        report = _run_report()
        passing = {c.code for c in report.checks if c.status == "passed"}
        assert "mvp_scenarios_active" in passing

    def test_mvp_scenarios_active_check_exists_in_report(self) -> None:
        report = _run_report()
        check_codes = {c.code for c in report.checks}
        assert "mvp_scenarios_active" in check_codes


class TestCiiVisualReadinessGuardrails:
    def test_non_geometric_aggregation_produces_critical_issue(self) -> None:
        bad = [
            {
                "country_slug": "russia",
                "scenario_slug": "relocation_residence",
                "aggregation_method": "arithmetic",
            }
        ]
        report = _run_report(list_cii_scores_with_non_geometric_aggregation=bad)
        codes = {i.code for i in report.issues}
        assert "cii_aggregation_method_not_geometric" in codes
        assert report.valid is False

    def test_geometric_aggregation_check_passes_when_all_geometric(self) -> None:
        report = _run_report()
        passing = {c.code for c in report.checks if c.status == "passed"}
        assert "cii_scores_use_geometric_aggregation" in passing

    def test_metric_without_polarity_produces_critical_issue(self) -> None:
        no_polarity = [{"slug": "rule_of_law", "polarity": None}]
        report = _run_report(list_cii_metric_definitions_without_polarity=no_polarity)
        codes = {i.code for i in report.issues}
        assert "cii_metric_polarity_missing" in codes
        assert report.valid is False

    def test_metric_polarity_check_passes_when_all_have_polarity(self) -> None:
        report = _run_report()
        passing = {c.code for c in report.checks if c.status == "passed"}
        assert "cii_metric_definitions_have_polarity" in passing

    def test_all_cii_visual_readiness_checks_present(self) -> None:
        report = _run_report()
        check_codes = {c.code for c in report.checks}
        expected = {
            "cii_scores_use_geometric_aggregation",
            "cii_metric_definitions_have_polarity",
        }
        assert expected.issubset(check_codes)


class TestLegalTimelineGuardrails:
    def test_country_without_legal_events_produces_critical_issue(self) -> None:
        missing = [{"country_slug": "russia"}]
        report = _run_report(list_mvp_countries_without_legal_events=missing)
        codes = {i.code for i in report.issues}
        assert "legal_timeline_no_events_for_country" in codes
        assert report.valid is False

    def test_legal_timeline_check_passes_when_all_countries_have_events(self) -> None:
        report = _run_report()
        passing = {c.code for c in report.checks if c.status == "passed"}
        assert "legal_timeline_has_events_per_country" in passing

    def test_legal_timeline_check_exists_in_report(self) -> None:
        report = _run_report()
        check_codes = {c.code for c in report.checks}
        assert "legal_timeline_has_events_per_country" in check_codes


class TestGuardrailsDoNotMaskCriticalIssues:
    def test_multiple_visual_guardrail_failures_all_appear(self) -> None:
        report = _run_report(
            list_inactive_mvp_scenarios=[{"scenario_slug": "low_budget_living"}],
            list_cii_metric_definitions_without_polarity=[
                {"slug": "safety", "polarity": None}
            ],
            list_mvp_countries_without_legal_events=[{"country_slug": "uruguay"}],
        )
        codes = {i.code for i in report.issues}
        assert "mvp_scenario_inactive" in codes
        assert "cii_metric_polarity_missing" in codes
        assert "legal_timeline_no_events_for_country" in codes
        assert report.valid is False
        assert report.critical_issues_count == 3

    def test_clean_report_passes_all_new_checks(self) -> None:
        report = _run_report()
        assert report.valid is True
        failed = [c.code for c in report.checks if c.status == "failed"]
        assert failed == []


class TestSyntheticUserStoryRussianNotes:
    def test_russian_synthetic_notes_are_accepted(self) -> None:
        report = _run_report(list_invalid_synthetic_user_stories=[])
        assert report.valid is True

    def test_story_without_any_marking_is_invalid(self) -> None:
        invalid = [
            {
                "id": "story-id",
                "verification_status": "synthetic",
                "is_synthetic": True,
                "notes": "Обычная история.",
            }
        ]
        report = _run_report(list_invalid_synthetic_user_stories=invalid)
        codes = {i.code for i in report.issues}
        assert "synthetic_user_story_invalid" in codes
        assert report.valid is False
