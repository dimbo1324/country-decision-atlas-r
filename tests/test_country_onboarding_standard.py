from typing import Any
from unittest.mock import MagicMock, patch


_REPO = "app.repositories.country_onboarding"
_SVC = "app.services.country_onboarding"
_DQ_SVC = "app.services.data_quality"


def _make_connection() -> MagicMock:
    return MagicMock()


def _full_pass_defaults(country_slug: str = "russia") -> dict[str, Any]:
    return {
        "get_country_base": {
            "id": "1",
            "slug": country_slug,
            "name": "Russia",
            "iso2": "RU",
            "is_active": True,
        },
        "count_published_country_cards": 2,
        "count_active_cii_metrics": 6,
        "count_country_cii_metric_values": 6,
        "count_cii_scenario_scores": 5,
        "count_published_sources": 20,
        "count_published_evidence": 30,
        "count_published_legal_signals": 10,
        "count_timeline_events": 12,
        "count_timeline_events_with_traceability": 12,
        "check_localization_metadata": True,
    }


def _evaluate(country_slug: str = "russia", **overrides: Any) -> Any:
    from app.services.country_onboarding import evaluate_country_onboarding

    defaults = _full_pass_defaults(country_slug)
    defaults.update(overrides)
    patchers = {}
    for name, value in defaults.items():
        patchers[name] = MagicMock(return_value=value)
    with patch.multiple(_REPO, **patchers):
        return evaluate_country_onboarding(_make_connection(), country_slug)


def _run_dq_with_onboarding(**onboarding_override: Any) -> Any:
    from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
    from app.services.data_quality import build_data_quality_report

    onboarding_checks: list[DataQualityCheck] = onboarding_override.get("checks", [])
    onboarding_issues: list[DataQualityIssue] = onboarding_override.get("issues", [])

    dq_repo = "app.repositories.data_quality"
    empty: list[Any] = []
    repo_patches = {
        "list_missing_mvp_countries": MagicMock(return_value=empty),
        "list_published_countries_without_cards": MagicMock(return_value=empty),
        "list_published_countries_without_sources": MagicMock(return_value=empty),
        "list_mvp_countries_with_too_few_published_sources": MagicMock(
            return_value=empty
        ),
        "list_mvp_countries_with_too_few_published_evidence": MagicMock(
            return_value=empty
        ),
        "list_mvp_countries_with_too_few_published_legal_signals": MagicMock(
            return_value=empty
        ),
        "list_missing_country_scores_for_required_scenarios": MagicMock(
            return_value=empty
        ),
        "list_scores_without_breakdowns": MagicMock(return_value=empty),
        "list_scores_with_incomplete_breakdowns": MagicMock(return_value=empty),
        "list_scores_with_invalid_weight_sum": MagicMock(return_value=empty),
        "list_published_score_breakdowns_without_source_ids": MagicMock(
            return_value=empty
        ),
        "list_published_legal_signals_without_source": MagicMock(return_value=empty),
        "list_published_legal_signals_without_evidence": MagicMock(return_value=empty),
        "list_published_legal_signals_without_timeline_event": MagicMock(
            return_value=empty
        ),
        "list_timeline_events_with_invalid_date": MagicMock(return_value=empty),
        "list_timeline_events_with_invalid_impact_direction": MagicMock(
            return_value=empty
        ),
        "list_timeline_events_with_invalid_impact_level": MagicMock(return_value=empty),
        "list_timeline_events_with_country_mismatch": MagicMock(return_value=empty),
        "list_timeline_events_without_traceability": MagicMock(return_value=empty),
        "list_unplanned_future_timeline_events": MagicMock(return_value=empty),
        "list_evidence_without_source": MagicMock(return_value=empty),
        "list_evidence_without_country": MagicMock(return_value=empty),
        "list_published_sources_with_missing_required_fields": MagicMock(
            return_value=empty
        ),
        "list_published_sources_with_example_invalid_url": MagicMock(
            return_value=empty
        ),
        "list_invalid_synthetic_user_stories": MagicMock(return_value=empty),
        "list_country_cards_with_empty_major_sections": MagicMock(return_value=empty),
        "list_country_cards_with_demo_source_summary": MagicMock(return_value=empty),
        "list_mvp_countries_missing_cii": MagicMock(return_value=empty),
        "list_cii_scores_missing_formula_metadata": MagicMock(return_value=empty),
        "list_cii_metric_weights_with_invalid_sum": MagicMock(return_value=empty),
        "list_mvp_metrics_missing_values": MagicMock(return_value=empty),
        "list_cii_scores_out_of_range": MagicMock(return_value=empty),
        "list_mvp_scenarios_missing_cii_weights": MagicMock(return_value=empty),
        "list_cii_scenario_weights_with_negative_values": MagicMock(return_value=empty),
        "list_cii_scenario_weights_exceeding_one": MagicMock(return_value=empty),
        "list_mvp_scenarios_missing_cii_scores": MagicMock(return_value=empty),
        "list_cii_scenario_scores_missing_formula_metadata": MagicMock(
            return_value=empty
        ),
        "list_inactive_mvp_scenarios": MagicMock(return_value=empty),
        "list_cii_scores_with_non_geometric_aggregation": MagicMock(return_value=empty),
        "list_cii_metric_definitions_without_polarity": MagicMock(return_value=empty),
        "list_mvp_countries_without_legal_events": MagicMock(return_value=empty),
    }
    with (
        patch(f"{_DQ_SVC}.build_translation_quality_results", return_value=([], [])),
        patch(
            f"{_DQ_SVC}.build_country_onboarding_dq_results",
            return_value=(onboarding_checks, onboarding_issues),
        ),
        patch.multiple(dq_repo, **repo_patches),
    ):
        return build_data_quality_report(_make_connection())


class TestRussiaPassesOnboardingStandard:
    def test_russia_is_mvp_ready(self) -> None:
        result = _evaluate("russia")
        assert result.mvp_ready is True

    def test_russia_has_no_findings(self) -> None:
        result = _evaluate("russia")
        assert result.findings == []

    def test_russia_all_sections_ready(self) -> None:
        result = _evaluate("russia")
        for section in result.sections.values():
            assert section.status == "ready"


class TestUruguayPassesOnboardingStandard:
    def test_uruguay_is_mvp_ready(self) -> None:
        result = _evaluate("uruguay")
        assert result.mvp_ready is True

    def test_uruguay_has_no_findings(self) -> None:
        result = _evaluate("uruguay")
        assert result.findings == []

    def test_uruguay_all_sections_ready(self) -> None:
        result = _evaluate("uruguay")
        for section in result.sections.values():
            assert section.status == "ready"


class TestMissingCountryCard:
    def test_missing_card_produces_critical_finding(self) -> None:
        result = _evaluate(count_published_country_cards=0)
        codes = {f.code for f in result.findings}
        assert "country_onboarding_country_card_exists" in codes

    def test_missing_card_sets_mvp_ready_false(self) -> None:
        result = _evaluate(count_published_country_cards=0)
        assert result.mvp_ready is False

    def test_missing_card_section_status_is_missing(self) -> None:
        result = _evaluate(count_published_country_cards=0)
        assert result.sections["country_card"].status == "missing"

    def test_missing_card_severity_is_critical(self) -> None:
        result = _evaluate(count_published_country_cards=0)
        assert result.sections["country_card"].severity == "critical"


class TestMissingCiiMetrics:
    def test_missing_metrics_produces_critical_finding(self) -> None:
        result = _evaluate(
            count_country_cii_metric_values=3, count_active_cii_metrics=6
        )
        codes = {f.code for f in result.findings}
        assert "country_onboarding_cii_metrics_complete" in codes

    def test_missing_metrics_sets_mvp_ready_false(self) -> None:
        result = _evaluate(
            count_country_cii_metric_values=0, count_active_cii_metrics=6
        )
        assert result.mvp_ready is False

    def test_missing_metrics_section_shows_correct_counts(self) -> None:
        result = _evaluate(
            count_country_cii_metric_values=4, count_active_cii_metrics=6
        )
        section = result.sections["cii_metrics"]
        assert section.required == 6
        assert section.actual == 4
        assert section.missing == 2

    def test_zero_metrics_is_critical(self) -> None:
        result = _evaluate(
            count_country_cii_metric_values=0, count_active_cii_metrics=6
        )
        assert result.sections["cii_metrics"].severity == "critical"


class TestMissingScenarioScores:
    def test_missing_scores_produces_critical_finding(self) -> None:
        result = _evaluate(count_cii_scenario_scores=3)
        codes = {f.code for f in result.findings}
        assert "country_onboarding_scenario_scores_complete" in codes

    def test_missing_scores_sets_mvp_ready_false(self) -> None:
        result = _evaluate(count_cii_scenario_scores=0)
        assert result.mvp_ready is False

    def test_missing_scores_section_shows_correct_counts(self) -> None:
        result = _evaluate(count_cii_scenario_scores=2)
        section = result.sections["scenario_scores"]
        assert section.required == 5
        assert section.actual == 2
        assert section.missing == 3


class TestInsufficientSources:
    def test_too_few_sources_produces_critical_finding(self) -> None:
        result = _evaluate(count_published_sources=5)
        codes = {f.code for f in result.findings}
        assert "country_onboarding_sources_threshold" in codes

    def test_too_few_sources_sets_mvp_ready_false(self) -> None:
        result = _evaluate(count_published_sources=0)
        assert result.mvp_ready is False

    def test_exactly_minimum_sources_passes(self) -> None:
        result = _evaluate(count_published_sources=10)
        assert result.sections["sources"].status == "ready"

    def test_below_minimum_sources_shows_missing_count(self) -> None:
        result = _evaluate(count_published_sources=7)
        section = result.sections["sources"]
        assert section.missing == 3


class TestInsufficientEvidence:
    def test_too_few_evidence_produces_critical_finding(self) -> None:
        result = _evaluate(count_published_evidence=5)
        codes = {f.code for f in result.findings}
        assert "country_onboarding_evidence_threshold" in codes

    def test_too_few_evidence_sets_mvp_ready_false(self) -> None:
        result = _evaluate(count_published_evidence=0)
        assert result.mvp_ready is False

    def test_exactly_minimum_evidence_passes(self) -> None:
        result = _evaluate(count_published_evidence=15)
        assert result.sections["evidence"].status == "ready"


class TestMissingLegalSignals:
    def test_too_few_legal_signals_produces_critical_finding(self) -> None:
        result = _evaluate(count_published_legal_signals=2)
        codes = {f.code for f in result.findings}
        assert "country_onboarding_legal_signals_threshold" in codes

    def test_zero_legal_signals_sets_mvp_ready_false(self) -> None:
        result = _evaluate(count_published_legal_signals=0)
        assert result.mvp_ready is False

    def test_exactly_minimum_legal_signals_passes(self) -> None:
        result = _evaluate(count_published_legal_signals=5)
        assert result.sections["legal_signals"].status == "ready"


class TestMissingTimelineEvents:
    def test_too_few_timeline_events_produces_critical_finding(self) -> None:
        result = _evaluate(
            count_timeline_events=2, count_timeline_events_with_traceability=2
        )
        codes = {f.code for f in result.findings}
        assert "country_onboarding_timeline_events_threshold" in codes

    def test_zero_timeline_events_sets_mvp_ready_false(self) -> None:
        result = _evaluate(
            count_timeline_events=0, count_timeline_events_with_traceability=0
        )
        assert result.mvp_ready is False

    def test_exactly_minimum_timeline_events_passes(self) -> None:
        result = _evaluate(
            count_timeline_events=5, count_timeline_events_with_traceability=5
        )
        assert result.sections["timeline"].status == "ready"


class TestTimelineEventSourceBacked:
    def test_event_without_source_produces_critical_finding(self) -> None:
        result = _evaluate(
            count_timeline_events=8, count_timeline_events_with_traceability=6
        )
        codes = {f.code for f in result.findings}
        assert "country_onboarding_timeline_events_source_backed" in codes

    def test_event_without_source_sets_mvp_ready_false(self) -> None:
        result = _evaluate(
            count_timeline_events=5, count_timeline_events_with_traceability=4
        )
        assert result.mvp_ready is False

    def test_all_events_sourced_passes(self) -> None:
        result = _evaluate(
            count_timeline_events=10, count_timeline_events_with_traceability=10
        )
        assert result.sections["timeline"].status == "ready"

    def test_source_backed_missing_count_is_correct(self) -> None:
        result = _evaluate(
            count_timeline_events=10, count_timeline_events_with_traceability=7
        )
        section = result.sections["timeline"]
        assert section.missing == 3


class TestMatrixReadiness:
    def test_missing_scenario_scores_blocks_matrix(self) -> None:
        result = _evaluate(count_cii_scenario_scores=3)
        assert result.sections["matrix"].status == "blocked"

    def test_all_scenario_scores_enables_matrix(self) -> None:
        result = _evaluate(count_cii_scenario_scores=5)
        assert result.sections["matrix"].status == "ready"

    def test_matrix_blocked_produces_critical_finding(self) -> None:
        result = _evaluate(count_cii_scenario_scores=0)
        codes = {f.code for f in result.findings}
        assert "country_onboarding_visual_matrix_ready" in codes


class TestHomeOverviewReadiness:
    def test_no_cii_blocks_home_overview(self) -> None:
        result = _evaluate(count_cii_scenario_scores=0)
        assert result.sections["home_overview"].status == "blocked"

    def test_no_timeline_blocks_home_overview(self) -> None:
        result = _evaluate(
            count_timeline_events=0, count_timeline_events_with_traceability=0
        )
        assert result.sections["home_overview"].status == "blocked"

    def test_no_card_blocks_home_overview(self) -> None:
        result = _evaluate(count_published_country_cards=0)
        assert result.sections["home_overview"].status == "blocked"

    def test_all_prerequisites_enable_home_overview(self) -> None:
        result = _evaluate()
        assert result.sections["home_overview"].status == "ready"

    def test_home_overview_blocked_produces_critical_finding(self) -> None:
        result = _evaluate(count_cii_scenario_scores=0)
        codes = {f.code for f in result.findings}
        assert "country_onboarding_home_overview_ready" in codes


class TestLocalizationReadiness:
    def test_missing_localization_produces_critical_finding(self) -> None:
        result = _evaluate(check_localization_metadata=False)
        codes = {f.code for f in result.findings}
        assert "country_onboarding_localization_ready" in codes

    def test_missing_localization_sets_mvp_ready_false(self) -> None:
        result = _evaluate(check_localization_metadata=False)
        assert result.mvp_ready is False

    def test_present_localization_section_is_ready(self) -> None:
        result = _evaluate(check_localization_metadata=True)
        assert result.sections["localization"].status == "ready"


class TestEvaluateAllMvpCountries:
    def test_all_mvp_ready_when_both_pass(self) -> None:
        from app.services.country_onboarding import evaluate_all_mvp_countries

        defaults = _full_pass_defaults()
        patchers = {
            name: MagicMock(return_value=value) for name, value in defaults.items()
        }
        with patch.multiple(_REPO, **patchers):
            result = evaluate_all_mvp_countries(_make_connection())
        assert result.all_mvp_ready is True
        assert len(result.countries) == 3

    def test_not_all_ready_when_one_fails(self) -> None:
        from app.services.country_onboarding import evaluate_all_mvp_countries

        call_count = [0]

        def get_country_base_side_effect(*_: Any, **__: Any) -> dict[str, Any]:
            call_count[0] += 1
            if call_count[0] == 1:
                return {
                    "id": "1",
                    "slug": "russia",
                    "name": "Russia",
                    "iso2": "RU",
                    "is_active": True,
                }
            return None  # type: ignore[return-value]

        defaults = _full_pass_defaults()
        patchers = {
            name: MagicMock(return_value=value) for name, value in defaults.items()
        }
        patchers["get_country_base"] = MagicMock(
            side_effect=get_country_base_side_effect
        )
        with patch.multiple(_REPO, **patchers):
            result = evaluate_all_mvp_countries(_make_connection())
        assert result.all_mvp_ready is False


class TestDataQualityIntegration:
    def test_clean_report_has_no_onboarding_issues(self) -> None:
        report = _run_dq_with_onboarding()
        onboarding_issue_codes = {
            i.code for i in report.issues if i.code.startswith("country_onboarding_")
        }
        assert onboarding_issue_codes == set()

    def test_dq_report_includes_onboarding_checks(self) -> None:
        from app.schemas.data_quality import DataQualityCheck

        onboarding_checks = [
            DataQualityCheck(code="country_onboarding_mvp_ready", status="passed")
        ]
        report = _run_dq_with_onboarding(checks=onboarding_checks)
        check_codes = {c.code for c in report.checks}
        assert "country_onboarding_mvp_ready" in check_codes

    def test_onboarding_critical_issue_invalidates_dq_report(self) -> None:
        from app.schemas.data_quality import DataQualityIssue

        onboarding_issues = [
            DataQualityIssue(
                code="country_onboarding_cii_metrics_complete",
                severity="critical",
                entity_type="country",
                entity_id="argentina",
                message="[argentina] Missing CII metrics.",
                details={"country_slug": "argentina"},
            )
        ]
        report = _run_dq_with_onboarding(issues=onboarding_issues)
        assert report.valid is False
        assert report.critical_issues_count >= 1

    def test_onboarding_check_codes_match_spec(self) -> None:
        from app.schemas.data_quality import DataQualityCheck

        expected_codes = [
            "country_onboarding_country_card_exists",
            "country_onboarding_cii_metrics_complete",
            "country_onboarding_scenario_scores_complete",
            "country_onboarding_sources_threshold",
            "country_onboarding_evidence_threshold",
            "country_onboarding_legal_signals_threshold",
            "country_onboarding_timeline_events_threshold",
            "country_onboarding_timeline_events_source_backed",
            "country_onboarding_visual_matrix_ready",
            "country_onboarding_home_overview_ready",
            "country_onboarding_localization_ready",
            "country_onboarding_mvp_ready",
        ]
        onboarding_checks = [
            DataQualityCheck(code=code, status="passed") for code in expected_codes
        ]
        report = _run_dq_with_onboarding(checks=onboarding_checks)
        check_codes = {c.code for c in report.checks}
        for code in expected_codes:
            assert code in check_codes

    def test_country_onboarding_issues_include_required_actual_missing(self) -> None:
        from app.schemas.data_quality import DataQualityIssue

        issue = DataQualityIssue(
            code="country_onboarding_sources_threshold",
            severity="critical",
            entity_type="country",
            entity_id="argentina",
            message="[argentina] Country has 5 published sources; 10 required.",
            details={
                "country_slug": "argentina",
                "required": 10,
                "actual": 5,
                "missing": 5,
            },
        )
        report = _run_dq_with_onboarding(issues=[issue])
        matching = [
            i for i in report.issues if i.code == "country_onboarding_sources_threshold"
        ]
        assert len(matching) == 1
        assert matching[0].details.get("required") == 10
        assert matching[0].details.get("actual") == 5
        assert matching[0].details.get("missing") == 5


class TestThresholdValues:
    def test_required_cii_metrics_threshold(self) -> None:
        from app.services.country_onboarding import COUNTRY_ONBOARDING_THRESHOLDS

        assert COUNTRY_ONBOARDING_THRESHOLDS["required_cii_metrics"] == 6

    def test_required_scenario_scores_threshold(self) -> None:
        from app.services.country_onboarding import COUNTRY_ONBOARDING_THRESHOLDS

        assert COUNTRY_ONBOARDING_THRESHOLDS["required_scenario_scores"] == 5

    def test_minimum_sources_threshold(self) -> None:
        from app.services.country_onboarding import COUNTRY_ONBOARDING_THRESHOLDS

        assert COUNTRY_ONBOARDING_THRESHOLDS["minimum_sources"] == 10

    def test_minimum_evidence_threshold(self) -> None:
        from app.services.country_onboarding import COUNTRY_ONBOARDING_THRESHOLDS

        assert COUNTRY_ONBOARDING_THRESHOLDS["minimum_evidence_items"] == 15

    def test_minimum_legal_signals_threshold(self) -> None:
        from app.services.country_onboarding import COUNTRY_ONBOARDING_THRESHOLDS

        assert COUNTRY_ONBOARDING_THRESHOLDS["minimum_legal_signals"] == 5

    def test_minimum_timeline_events_threshold(self) -> None:
        from app.services.country_onboarding import COUNTRY_ONBOARDING_THRESHOLDS

        assert COUNTRY_ONBOARDING_THRESHOLDS["minimum_timeline_events"] == 5

    def test_timeline_events_source_ratio_is_full(self) -> None:
        from app.services.country_onboarding import COUNTRY_ONBOARDING_THRESHOLDS

        assert COUNTRY_ONBOARDING_THRESHOLDS["timeline_events_with_source_ratio"] == 1.0

    def test_country_card_required(self) -> None:
        from app.services.country_onboarding import COUNTRY_ONBOARDING_THRESHOLDS

        assert COUNTRY_ONBOARDING_THRESHOLDS["country_card_required"] is True

    def test_localization_required(self) -> None:
        from app.services.country_onboarding import COUNTRY_ONBOARDING_THRESHOLDS

        assert COUNTRY_ONBOARDING_THRESHOLDS["localization_metadata_required"] is True

    def test_matrix_ready_required(self) -> None:
        from app.services.country_onboarding import COUNTRY_ONBOARDING_THRESHOLDS

        assert COUNTRY_ONBOARDING_THRESHOLDS["matrix_ready_required"] is True

    def test_home_overview_ready_required(self) -> None:
        from app.services.country_onboarding import COUNTRY_ONBOARDING_THRESHOLDS

        assert COUNTRY_ONBOARDING_THRESHOLDS["home_overview_ready_required"] is True
