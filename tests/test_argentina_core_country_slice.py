"""Argentina exists, is active, and has a complete country card."""

from typing import Any
from unittest.mock import MagicMock, patch


_REPO = "app.repositories.country_onboarding"
_SVC = "app.services.country_onboarding"


def _make_connection() -> MagicMock:
    return MagicMock()


def _argentina_incomplete_defaults() -> dict[str, Any]:
    return {
        "get_country_base": {
            "id": "arg-id",
            "slug": "argentina",
            "name": "Argentina",
            "iso2": "AR",
            "is_active": True,
        },
        "count_published_country_cards": 2,
        "count_active_cii_metrics": 6,
        "count_country_cii_metric_values": 0,
        "count_cii_scenario_scores": 0,
        "count_published_sources": 6,
        "count_published_evidence": 6,
        "count_published_legal_signals": 0,
        "count_timeline_events": 0,
        "count_timeline_events_with_traceability": 0,
        "check_localization_metadata": True,
    }


def _russia_pass_defaults() -> dict[str, Any]:
    return {
        "get_country_base": {
            "id": "ru-id",
            "slug": "russia",
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


def _argentina_complete_defaults() -> dict[str, Any]:
    return {
        "get_country_base": {
            "id": "arg-id",
            "slug": "argentina",
            "name": "Argentina",
            "iso2": "AR",
            "is_active": True,
        },
        "count_published_country_cards": 2,
        "count_active_cii_metrics": 6,
        "count_country_cii_metric_values": 6,
        "count_cii_scenario_scores": 5,
        "count_published_sources": 10,
        "count_published_evidence": 15,
        "count_published_legal_signals": 6,
        "count_timeline_events": 6,
        "count_timeline_events_with_traceability": 6,
        "check_localization_metadata": True,
    }


def _evaluate_argentina(**overrides: Any) -> Any:
    from app.services.country_onboarding import evaluate_country_onboarding

    defaults = _argentina_incomplete_defaults()
    defaults.update(overrides)
    patchers = {k: MagicMock(return_value=v) for k, v in defaults.items()}
    with patch.multiple(_REPO, **patchers):
        return evaluate_country_onboarding(_make_connection(), "argentina")


class TestArgentinaExistsAndIsActive:
    def test_argentina_has_base_row(self) -> None:
        result = _evaluate_argentina()
        assert result.country_slug == "argentina"
        assert result.sections["base"].status == "ready"

    def test_argentina_missing_returns_missing_status(self) -> None:
        result = _evaluate_argentina(get_country_base=None)
        assert result.mvp_ready is False
        assert result.sections["base"].status == "missing"


class TestArgentinaCountryCard:
    def test_argentina_with_cards_passes_card_section(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["country_card"].status == "ready"
        assert result.sections["country_card"].actual == 2

    def test_argentina_without_cards_fails_card_section(self) -> None:
        result = _evaluate_argentina(count_published_country_cards=0)
        assert result.sections["country_card"].status == "missing"
        assert result.mvp_ready is False


class TestArgentinaIsIncomplete:
    def test_argentina_is_not_mvp_ready(self) -> None:
        result = _evaluate_argentina()
        assert result.mvp_ready is False

    def test_argentina_missing_cii_metrics(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["cii_metrics"].status == "missing"
        assert result.sections["cii_metrics"].actual == 0
        assert result.sections["cii_metrics"].missing == 6

    def test_argentina_missing_scenario_scores(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["scenario_scores"].status == "missing"
        assert result.sections["scenario_scores"].actual == 0

    def test_argentina_insufficient_sources(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["sources"].status == "incomplete"
        assert result.sections["sources"].actual == 6
        assert result.sections["sources"].missing == 4

    def test_argentina_insufficient_evidence(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["evidence"].status == "incomplete"
        assert result.sections["evidence"].actual == 6
        assert result.sections["evidence"].missing == 9

    def test_argentina_missing_legal_signals(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["legal_signals"].status == "missing"
        assert result.sections["legal_signals"].actual == 0

    def test_argentina_missing_timeline_events(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["timeline"].status == "missing"
        assert result.sections["timeline"].actual == 0

    def test_argentina_matrix_blocked(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["matrix"].status == "blocked"

    def test_argentina_home_overview_blocked(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["home_overview"].status == "blocked"

    def test_argentina_localization_ready(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["localization"].status == "ready"

    def test_argentina_has_findings(self) -> None:
        result = _evaluate_argentina()
        assert len(result.findings) > 0

    def test_argentina_finding_codes_are_present(self) -> None:
        result = _evaluate_argentina()
        codes = {f.code for f in result.findings}
        assert "country_onboarding_cii_metrics_complete" in codes
        assert "country_onboarding_scenario_scores_complete" in codes
        assert "country_onboarding_legal_signals_threshold" in codes
        assert "country_onboarding_timeline_events_threshold" in codes


class TestMvpCountrySlugsArchitecture:
    def test_argentina_in_mvp_country_slugs(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert "argentina" in MVP_COUNTRY_SLUGS

    def test_onboarding_country_slugs_is_empty(self) -> None:
        from app.repositories.data_quality import ONBOARDING_COUNTRY_SLUGS

        assert len(ONBOARDING_COUNTRY_SLUGS) == 0

    def test_mvp_country_slugs_has_three_countries(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert len(MVP_COUNTRY_SLUGS) == 3


class TestAllMvpCountriesWithArgentinaPromoted:
    def _run_all_mvp(
        self,
        russia_defaults: dict[str, Any],
        uruguay_defaults: dict[str, Any],
        argentina_defaults: dict[str, Any],
    ) -> Any:
        from app.services.country_onboarding import evaluate_all_mvp_countries

        conn = _make_connection()

        def make_evaluate(slug_map: dict[str, dict[str, Any]]) -> Any:
            from app.services.country_onboarding import (
                evaluate_country_onboarding as real_eval,
            )

            def _eval(connection: Any, slug: str) -> Any:
                defaults = slug_map.get(slug, _argentina_incomplete_defaults())
                patchers = {k: MagicMock(return_value=v) for k, v in defaults.items()}
                with patch.multiple(_REPO, **patchers):
                    return real_eval(connection, slug)

            return _eval

        slug_map = {
            "russia": russia_defaults,
            "uruguay": uruguay_defaults,
            "argentina": argentina_defaults,
        }

        with patch(
            f"{_SVC}.evaluate_country_onboarding", side_effect=make_evaluate(slug_map)
        ):
            return evaluate_all_mvp_countries(conn)

    def test_all_mvp_ready_true_when_all_three_pass(self) -> None:
        ru = _russia_pass_defaults()
        uy = {
            **_russia_pass_defaults(),
            "get_country_base": {
                "id": "uy-id",
                "slug": "uruguay",
                "name": "Uruguay",
                "iso2": "UY",
                "is_active": True,
            },
        }
        ar = _argentina_complete_defaults()
        result = self._run_all_mvp(ru, uy, ar)
        assert result.all_mvp_ready is True

    def test_all_mvp_ready_false_when_russia_fails(self) -> None:
        ru = {**_russia_pass_defaults(), "count_cii_scenario_scores": 0}
        uy = {
            **_russia_pass_defaults(),
            "get_country_base": {
                "id": "uy-id",
                "slug": "uruguay",
                "name": "Uruguay",
                "iso2": "UY",
                "is_active": True,
            },
        }
        ar = _argentina_complete_defaults()
        result = self._run_all_mvp(ru, uy, ar)
        assert result.all_mvp_ready is False

    def test_mvp_countries_includes_argentina(self) -> None:
        ru = _russia_pass_defaults()
        uy = {
            **_russia_pass_defaults(),
            "get_country_base": {
                "id": "uy-id",
                "slug": "uruguay",
                "name": "Uruguay",
                "iso2": "UY",
                "is_active": True,
            },
        }
        ar = _argentina_complete_defaults()
        result = self._run_all_mvp(ru, uy, ar)
        assert any(r.country_slug == "argentina" for r in result.countries)

    def test_onboarding_countries_is_empty(self) -> None:
        ru = _russia_pass_defaults()
        uy = {
            **_russia_pass_defaults(),
            "get_country_base": {
                "id": "uy-id",
                "slug": "uruguay",
                "name": "Uruguay",
                "iso2": "UY",
                "is_active": True,
            },
        }
        ar = _argentina_complete_defaults()
        result = self._run_all_mvp(ru, uy, ar)
        assert len(result.onboarding_countries) == 0


class TestArgentinaDqIntegration:
    def test_argentina_incomplete_produces_warning_not_critical_dq_issues(self) -> None:
        from app.schemas.country_onboarding import (
            CountryOnboardingResult,
            OnboardingFinding,
        )
        from app.services.country_onboarding import build_country_onboarding_dq_results

        mvp_result_ru = CountryOnboardingResult(
            country_slug="russia", mvp_ready=True, sections={}, findings=[]
        )
        mvp_result_uy = CountryOnboardingResult(
            country_slug="uruguay", mvp_ready=True, sections={}, findings=[]
        )
        arg_result = CountryOnboardingResult(
            country_slug="argentina",
            mvp_ready=False,
            sections={},
            findings=[
                OnboardingFinding(
                    code="country_onboarding_cii_metrics_complete",
                    severity="critical",
                    message="Missing CII metrics.",
                )
            ],
        )

        from app.schemas.country_onboarding import AllCountriesOnboardingResult

        full_result = AllCountriesOnboardingResult(
            countries=[mvp_result_ru, mvp_result_uy],
            onboarding_countries=[arg_result],
            all_mvp_ready=True,
        )

        with patch(f"{_SVC}.evaluate_all_mvp_countries", return_value=full_result):
            _checks, issues = build_country_onboarding_dq_results(_make_connection())

        argentina_issues = [i for i in issues if i.entity_id == "argentina"]
        assert len(argentina_issues) > 0
        for issue in argentina_issues:
            assert issue.severity == "warning", (
                f"Expected warning, got {issue.severity}"
            )

    def test_argentina_dq_issues_do_not_fail_mvp_check_codes(self) -> None:
        from app.schemas.country_onboarding import (
            AllCountriesOnboardingResult,
            CountryOnboardingResult,
            OnboardingFinding,
        )
        from app.services.country_onboarding import build_country_onboarding_dq_results

        mvp_result_ru = CountryOnboardingResult(
            country_slug="russia", mvp_ready=True, sections={}, findings=[]
        )
        mvp_result_uy = CountryOnboardingResult(
            country_slug="uruguay", mvp_ready=True, sections={}, findings=[]
        )
        arg_result = CountryOnboardingResult(
            country_slug="argentina",
            mvp_ready=False,
            sections={},
            findings=[
                OnboardingFinding(
                    code="country_onboarding_cii_metrics_complete",
                    severity="critical",
                    message="Missing CII metrics.",
                )
            ],
        )

        full_result = AllCountriesOnboardingResult(
            countries=[mvp_result_ru, mvp_result_uy],
            onboarding_countries=[arg_result],
            all_mvp_ready=True,
        )

        with patch(f"{_SVC}.evaluate_all_mvp_countries", return_value=full_result):
            checks, _issues = build_country_onboarding_dq_results(_make_connection())

        check_map = {c.code: c.status for c in checks}
        assert check_map.get("country_onboarding_cii_metrics_complete") == "passed"

    def test_argentina_dq_issue_codes_are_prefixed_with_onboarding(self) -> None:
        from app.schemas.country_onboarding import (
            AllCountriesOnboardingResult,
            CountryOnboardingResult,
            OnboardingFinding,
        )
        from app.services.country_onboarding import build_country_onboarding_dq_results

        arg_result = CountryOnboardingResult(
            country_slug="argentina",
            mvp_ready=False,
            sections={},
            findings=[
                OnboardingFinding(
                    code="country_onboarding_sources_threshold",
                    severity="critical",
                    message="Too few sources.",
                )
            ],
        )

        full_result = AllCountriesOnboardingResult(
            countries=[],
            onboarding_countries=[arg_result],
            all_mvp_ready=True,
        )

        with patch(f"{_SVC}.evaluate_all_mvp_countries", return_value=full_result):
            _checks, issues = build_country_onboarding_dq_results(_make_connection())

        arg_issues = [i for i in issues if i.entity_id == "argentina"]
        for issue in arg_issues:
            assert issue.code.startswith("onboarding_")
