"""Closeout checks that all MVP countries (including Argentina) are fully onboarded."""

from typing import Any
from unittest.mock import MagicMock, patch


_REPO = "app.repositories.country_onboarding"


def _make_connection() -> MagicMock:
    return MagicMock()


def _argentina_mvp_defaults() -> dict[str, Any]:
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


def _russia_mvp_defaults() -> dict[str, Any]:
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


def _uruguay_mvp_defaults() -> dict[str, Any]:
    return {
        "get_country_base": {
            "id": "uy-id",
            "slug": "uruguay",
            "name": "Uruguay",
            "iso2": "UY",
            "is_active": True,
        },
        "count_published_country_cards": 2,
        "count_active_cii_metrics": 6,
        "count_country_cii_metric_values": 6,
        "count_cii_scenario_scores": 5,
        "count_published_sources": 20,
        "count_published_evidence": 15,
        "count_published_legal_signals": 10,
        "count_timeline_events": 10,
        "count_timeline_events_with_traceability": 10,
        "check_localization_metadata": True,
    }


def _run_all_three() -> Any:
    from app.services.country_onboarding import evaluate_all_mvp_countries

    _data: dict[str, dict[str, Any]] = {
        "argentina": _argentina_mvp_defaults(),
        "russia": _russia_mvp_defaults(),
        "uruguay": _uruguay_mvp_defaults(),
    }
    _ID = {"argentina": "arg-id", "russia": "ru-id", "uruguay": "uy-id"}
    _NAME = {"argentina": "Argentina", "russia": "Russia", "uruguay": "Uruguay"}
    _ISO2 = {"argentina": "AR", "russia": "RU", "uruguay": "UY"}

    with (
        patch(
            f"{_REPO}.get_country_base",
            side_effect=lambda _, slug: {
                "id": _ID[slug],
                "slug": slug,
                "name": _NAME[slug],
                "iso2": _ISO2[slug],
                "is_active": True,
            },
        ),
        patch(
            f"{_REPO}.count_published_country_cards",
            side_effect=lambda _, slug: _data[slug]["count_published_country_cards"],
        ),
        patch(f"{_REPO}.count_active_cii_metrics", side_effect=lambda _: 6),
        patch(
            f"{_REPO}.count_country_cii_metric_values",
            side_effect=lambda _, slug: _data[slug]["count_country_cii_metric_values"],
        ),
        patch(
            f"{_REPO}.count_cii_scenario_scores",
            side_effect=lambda _, slug, _sc: _data[slug]["count_cii_scenario_scores"],
        ),
        patch(
            f"{_REPO}.count_published_sources",
            side_effect=lambda _, slug: _data[slug]["count_published_sources"],
        ),
        patch(
            f"{_REPO}.count_published_evidence",
            side_effect=lambda _, slug: _data[slug]["count_published_evidence"],
        ),
        patch(
            f"{_REPO}.count_published_legal_signals",
            side_effect=lambda _, slug: _data[slug]["count_published_legal_signals"],
        ),
        patch(
            f"{_REPO}.count_timeline_events",
            side_effect=lambda _, slug: _data[slug]["count_timeline_events"],
        ),
        patch(
            f"{_REPO}.count_timeline_events_with_traceability",
            side_effect=lambda _, slug: _data[slug][
                "count_timeline_events_with_traceability"
            ],
        ),
        patch(
            f"{_REPO}.check_localization_metadata",
            side_effect=lambda _, _slug: True,
        ),
    ):
        return evaluate_all_mvp_countries(_make_connection())


class TestMvpCountrySlugConstants:
    def test_mvp_country_slugs_contains_russia(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert "russia" in MVP_COUNTRY_SLUGS

    def test_mvp_country_slugs_contains_uruguay(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert "uruguay" in MVP_COUNTRY_SLUGS

    def test_mvp_country_slugs_contains_argentina(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert "argentina" in MVP_COUNTRY_SLUGS

    def test_mvp_country_slugs_count_is_three(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert len(MVP_COUNTRY_SLUGS) == 3

    def test_onboarding_country_slugs_is_empty(self) -> None:
        from app.repositories.data_quality import ONBOARDING_COUNTRY_SLUGS

        assert len(ONBOARDING_COUNTRY_SLUGS) == 0


class TestArgentinaMvpReady:
    def test_argentina_mvp_ready_true(self) -> None:
        from app.services.country_onboarding import evaluate_country_onboarding

        defaults = _argentina_mvp_defaults()
        patchers = {k: MagicMock(return_value=v) for k, v in defaults.items()}
        with patch.multiple(_REPO, **patchers):
            result = evaluate_country_onboarding(_make_connection(), "argentina")
        assert result.mvp_ready is True

    def test_argentina_sources_ready(self) -> None:
        from app.services.country_onboarding import evaluate_country_onboarding

        defaults = _argentina_mvp_defaults()
        patchers = {k: MagicMock(return_value=v) for k, v in defaults.items()}
        with patch.multiple(_REPO, **patchers):
            result = evaluate_country_onboarding(_make_connection(), "argentina")
        assert result.sections["sources"].status == "ready"
        assert result.sections["sources"].actual == 10

    def test_argentina_evidence_ready(self) -> None:
        from app.services.country_onboarding import evaluate_country_onboarding

        defaults = _argentina_mvp_defaults()
        patchers = {k: MagicMock(return_value=v) for k, v in defaults.items()}
        with patch.multiple(_REPO, **patchers):
            result = evaluate_country_onboarding(_make_connection(), "argentina")
        assert result.sections["evidence"].status == "ready"
        assert result.sections["evidence"].actual == 15

    def test_argentina_legal_signals_ready(self) -> None:
        from app.services.country_onboarding import evaluate_country_onboarding

        defaults = _argentina_mvp_defaults()
        patchers = {k: MagicMock(return_value=v) for k, v in defaults.items()}
        with patch.multiple(_REPO, **patchers):
            result = evaluate_country_onboarding(_make_connection(), "argentina")
        assert result.sections["legal_signals"].status == "ready"
        assert result.sections["legal_signals"].actual == 6

    def test_argentina_timeline_ready(self) -> None:
        from app.services.country_onboarding import evaluate_country_onboarding

        defaults = _argentina_mvp_defaults()
        patchers = {k: MagicMock(return_value=v) for k, v in defaults.items()}
        with patch.multiple(_REPO, **patchers):
            result = evaluate_country_onboarding(_make_connection(), "argentina")
        assert result.sections["timeline"].status == "ready"
        assert result.sections["timeline"].actual == 6

    def test_argentina_cii_metrics_ready(self) -> None:
        from app.services.country_onboarding import evaluate_country_onboarding

        defaults = _argentina_mvp_defaults()
        patchers = {k: MagicMock(return_value=v) for k, v in defaults.items()}
        with patch.multiple(_REPO, **patchers):
            result = evaluate_country_onboarding(_make_connection(), "argentina")
        assert result.sections["cii_metrics"].status == "ready"

    def test_argentina_scenario_scores_ready(self) -> None:
        from app.services.country_onboarding import evaluate_country_onboarding

        defaults = _argentina_mvp_defaults()
        patchers = {k: MagicMock(return_value=v) for k, v in defaults.items()}
        with patch.multiple(_REPO, **patchers):
            result = evaluate_country_onboarding(_make_connection(), "argentina")
        assert result.sections["scenario_scores"].status == "ready"

    def test_argentina_has_no_findings(self) -> None:
        from app.services.country_onboarding import evaluate_country_onboarding

        defaults = _argentina_mvp_defaults()
        patchers = {k: MagicMock(return_value=v) for k, v in defaults.items()}
        with patch.multiple(_REPO, **patchers):
            result = evaluate_country_onboarding(_make_connection(), "argentina")
        assert len(result.findings) == 0


class TestAllMvpReadyCloseout:
    def test_all_mvp_ready_true_with_three_countries(self) -> None:
        result = _run_all_three()
        assert result.all_mvp_ready is True

    def test_mvp_countries_count_is_three(self) -> None:
        result = _run_all_three()
        assert len(result.countries) == 3

    def test_onboarding_countries_is_empty(self) -> None:
        result = _run_all_three()
        assert len(result.onboarding_countries) == 0

    def test_russia_in_mvp_countries(self) -> None:
        result = _run_all_three()
        slugs = [r.country_slug for r in result.countries]
        assert "russia" in slugs

    def test_uruguay_in_mvp_countries(self) -> None:
        result = _run_all_three()
        slugs = [r.country_slug for r in result.countries]
        assert "uruguay" in slugs

    def test_argentina_in_mvp_countries(self) -> None:
        result = _run_all_three()
        slugs = [r.country_slug for r in result.countries]
        assert "argentina" in slugs

    def test_russia_mvp_ready(self) -> None:
        result = _run_all_three()
        russia = next(r for r in result.countries if r.country_slug == "russia")
        assert russia.mvp_ready is True

    def test_uruguay_mvp_ready(self) -> None:
        result = _run_all_three()
        uruguay = next(r for r in result.countries if r.country_slug == "uruguay")
        assert uruguay.mvp_ready is True

    def test_argentina_mvp_ready(self) -> None:
        result = _run_all_three()
        argentina = next(r for r in result.countries if r.country_slug == "argentina")
        assert argentina.mvp_ready is True

    def test_all_mvp_ready_false_if_argentina_missing_legal(self) -> None:
        from app.services.country_onboarding import evaluate_country_onboarding

        ar_bad = {**_argentina_mvp_defaults(), "count_published_legal_signals": 0}

        def _svc_eval(conn: Any, slug: str) -> Any:
            if slug == "argentina":
                patchers = {k: MagicMock(return_value=v) for k, v in ar_bad.items()}
                with patch.multiple(_REPO, **patchers):
                    return evaluate_country_onboarding(conn, slug)
            defaults = (
                _russia_mvp_defaults() if slug == "russia" else _uruguay_mvp_defaults()
            )
            patchers = {k: MagicMock(return_value=v) for k, v in defaults.items()}
            with patch.multiple(_REPO, **patchers):
                return evaluate_country_onboarding(conn, slug)

        with patch(
            "app.services.country_onboarding.evaluate_country_onboarding",
            side_effect=_svc_eval,
        ):
            from app.services.country_onboarding import evaluate_all_mvp_countries

            result = evaluate_all_mvp_countries(_make_connection())
        assert result.all_mvp_ready is False


class TestMatrixThreeCountries:
    def test_cii_matrix_contains_three_mvp_countries(self) -> None:
        from app.services.cii_matrix import MVP_COUNTRIES

        assert len(MVP_COUNTRIES) == 3

    def test_cii_matrix_contains_russia(self) -> None:
        from app.services.cii_matrix import MVP_COUNTRIES

        assert "russia" in MVP_COUNTRIES

    def test_cii_matrix_contains_uruguay(self) -> None:
        from app.services.cii_matrix import MVP_COUNTRIES

        assert "uruguay" in MVP_COUNTRIES

    def test_cii_matrix_contains_argentina(self) -> None:
        from app.services.cii_matrix import MVP_COUNTRIES

        assert "argentina" in MVP_COUNTRIES

    def test_matrix_three_countries_times_five_scenarios_is_fifteen(self) -> None:
        from app.services.cii_matrix import MVP_COUNTRIES, MVP_SCENARIOS

        assert len(MVP_COUNTRIES) * len(MVP_SCENARIOS) == 15

    def test_matrix_has_five_scenarios(self) -> None:
        from app.services.cii_matrix import MVP_SCENARIOS

        assert len(MVP_SCENARIOS) == 5


class TestEpisodeCloseoutSlugIntegrity:
    def test_expansion_pipeline_complete_russia(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert "russia" in MVP_COUNTRY_SLUGS

    def test_expansion_pipeline_complete_uruguay(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert "uruguay" in MVP_COUNTRY_SLUGS

    def test_expansion_pipeline_complete_argentina(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert "argentina" in MVP_COUNTRY_SLUGS

    def test_no_countries_still_in_onboarding(self) -> None:
        from app.repositories.data_quality import ONBOARDING_COUNTRY_SLUGS

        assert len(ONBOARDING_COUNTRY_SLUGS) == 0
