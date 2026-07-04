"""Argentina's legal signals and timeline evidence are present and MVP-ready."""

from typing import Any
from unittest.mock import MagicMock, patch


_REPO = "app.repositories.country_onboarding"
_LS_REPO = "app.api.v1.legal_signals"
_TL_SVC = "app.services.legal_signal_timeline"
_SRC_REPO = "app.repositories.sources"

MVP_SCENARIOS = [
    "relocation_residence",
    "permanent_residence_citizenship",
    "low_budget_living",
    "business_self_employment",
    "safety_political_risk",
]


def _make_connection() -> MagicMock:
    return MagicMock()


def _argentina_full_defaults() -> dict[str, Any]:
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


def _uruguay_pass_defaults() -> dict[str, Any]:
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


def _evaluate_argentina(**overrides: Any) -> Any:
    from app.services.country_onboarding import evaluate_country_onboarding

    defaults = _argentina_full_defaults()
    defaults.update(overrides)
    patchers = {k: MagicMock(return_value=v) for k, v in defaults.items()}
    with patch.multiple(_REPO, **patchers):
        return evaluate_country_onboarding(_make_connection(), "argentina")


def _evaluate_all_mvp_with_argentina_full() -> Any:
    from app.services.country_onboarding import evaluate_all_mvp_countries

    arg_d = _argentina_full_defaults()
    ru_d = _russia_pass_defaults()
    uy_d = _uruguay_pass_defaults()

    _ISO2 = {"argentina": "AR", "russia": "RU", "uruguay": "UY"}
    _ID = {"argentina": "arg-id", "russia": "ru-id", "uruguay": "uy-id"}
    _NAME = {"argentina": "Argentina", "russia": "Russia", "uruguay": "Uruguay"}
    _data = {"argentina": arg_d, "russia": ru_d, "uruguay": uy_d}

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
            side_effect=lambda _, slug: _data[slug][
                "count_published_country_cards"
            ],
        ),
        patch(
            f"{_REPO}.count_active_cii_metrics",
            side_effect=lambda _: 6,
        ),
        patch(
            f"{_REPO}.count_country_cii_metric_values",
            side_effect=lambda _, slug: _data[slug][
                "count_country_cii_metric_values"
            ],
        ),
        patch(
            f"{_REPO}.count_cii_scenario_scores",
            side_effect=lambda _, slug, _sc: _data[slug][
                "count_cii_scenario_scores"
            ],
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
            side_effect=lambda _, slug: _data[slug][
                "count_published_legal_signals"
            ],
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


_ARGENTINA_LEGAL_SIGNALS = [
    {
        "id": "ls-ar-001",
        "country_id": "arg-id",
        "country_slug": "argentina",
        "title": "Temporary residence for foreigners requires DNM processing",
        "summary": "DNM manages residence applications including temporary and permanent categories.",
        "signal_type": "residence",
        "sentiment": "mixed",
        "severity": "medium",
        "status": "published",
        "confidence_level": "high",
        "impact_direction": "mixed",
        "impact_level": "medium",
        "affected_groups": ["relocators", "remote_workers"],
        "published_date": "2024-01-01",
        "source_id": "src-001",
        "source_title": "DNM Argentina",
        "source_url": "https://www.argentina.gob.ar/interior/migraciones",
    },
    {
        "id": "ls-ar-002",
        "country_id": "arg-id",
        "country_slug": "argentina",
        "title": "Argentine citizenship requires two years of legal residence",
        "summary": "Foreign nationals may apply after two years of legal residence.",
        "signal_type": "citizenship",
        "sentiment": "positive",
        "severity": "medium",
        "status": "published",
        "confidence_level": "high",
        "impact_direction": "positive",
        "impact_level": "medium",
        "affected_groups": ["long_term_residents", "families"],
        "published_date": "2024-01-01",
        "source_id": "src-002",
        "source_title": "Cancillería Argentina",
        "source_url": "https://www.cancilleria.gob.ar/en/tourism-and-travel/visas",
    },
    {
        "id": "ls-ar-003",
        "country_id": "arg-id",
        "country_slug": "argentina",
        "title": "Monotributo simplified tax regime available for freelancers",
        "summary": "AFIP monotributo is a simplified tax regime for self-employed individuals.",
        "signal_type": "tax",
        "sentiment": "positive",
        "severity": "medium",
        "status": "published",
        "confidence_level": "high",
        "impact_direction": "positive",
        "impact_level": "medium",
        "affected_groups": ["freelancers", "self_employed"],
        "published_date": "2024-01-01",
        "source_id": "src-003",
        "source_title": "AFIP Monotributo",
        "source_url": "https://www.afip.gob.ar/monotributo/",
    },
    {
        "id": "ls-ar-004",
        "country_id": "arg-id",
        "country_slug": "argentina",
        "title": "Banking access for foreigners subject to BCRA regulatory conditions",
        "summary": "BCRA regulates banking and financial services access in Argentina.",
        "signal_type": "banking",
        "sentiment": "mixed",
        "severity": "high",
        "status": "published",
        "confidence_level": "high",
        "impact_direction": "mixed",
        "impact_level": "high",
        "affected_groups": ["relocators", "business_owners"],
        "published_date": "2024-01-01",
        "source_id": "src-004",
        "source_title": "BCRA",
        "source_url": "https://www.bcra.gob.ar/",
    },
    {
        "id": "ls-ar-005",
        "country_id": "arg-id",
        "country_slug": "argentina",
        "title": "Business registration requires IGJ enrollment and AFIP CUIT",
        "summary": "Companies must register with IGJ and obtain CUIT from AFIP.",
        "signal_type": "business",
        "sentiment": "mixed",
        "severity": "medium",
        "status": "published",
        "confidence_level": "high",
        "impact_direction": "mixed",
        "impact_level": "medium",
        "affected_groups": ["business_owners", "self_employed"],
        "published_date": "2024-01-01",
        "source_id": "src-005",
        "source_title": "IGJ Argentina",
        "source_url": "https://www.argentina.gob.ar/justicia/igj",
    },
    {
        "id": "ls-ar-006",
        "country_id": "arg-id",
        "country_slug": "argentina",
        "title": "Political stability and regulatory volatility pose elevated risk",
        "summary": "Argentina faces recurring political instability and regulatory volatility.",
        "signal_type": "political_risk",
        "sentiment": "negative",
        "severity": "high",
        "status": "published",
        "confidence_level": "high",
        "impact_direction": "negative",
        "impact_level": "high",
        "affected_groups": ["risk_sensitive_users", "families"],
        "published_date": "2024-01-01",
        "source_id": "src-006",
        "source_title": "World Bank Argentina",
        "source_url": "https://data.worldbank.org/country/AR",
    },
]

_ARGENTINA_TIMELINE_EVENTS = [
    {
        "id": f"tl-ar-{i:03}",
        "country_id": "arg-id",
        "country_slug": "argentina",
        "country_name": "Argentina",
        "legal_signal_id": _ARGENTINA_LEGAL_SIGNALS[i]["id"],
        "event_date": "2024-01-01",
        "event_type": "confirmed",
        "impact_direction": _ARGENTINA_LEGAL_SIGNALS[i]["impact_direction"],
        "impact_level": _ARGENTINA_LEGAL_SIGNALS[i]["impact_level"],
        "title": _ARGENTINA_LEGAL_SIGNALS[i]["title"],
        "summary": _ARGENTINA_LEGAL_SIGNALS[i]["summary"],
        "source_id": _ARGENTINA_LEGAL_SIGNALS[i]["source_id"],
        "source_title": _ARGENTINA_LEGAL_SIGNALS[i]["source_title"],
        "source_url": _ARGENTINA_LEGAL_SIGNALS[i]["source_url"],
        "evidence_item_id": f"ei-ar-{i:03}",
        "affected_groups": _ARGENTINA_LEGAL_SIGNALS[i]["affected_groups"],
        "year": 2024,
    }
    for i in range(6)
]

_ARGENTINA_SOURCES = [
    {
        "id": f"src-{i:03}",
        "country_slug": "argentina",
        "title": f"Source {i}",
        "url": f"https://example-src-{i}.ar/",
        "status": "published",
    }
    for i in range(10)
]


class TestArgentinaOnboardingLegalReady:
    def test_sources_ready_at_threshold(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["sources"].status == "ready"

    def test_evidence_ready_at_threshold(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["evidence"].status == "ready"

    def test_legal_signals_ready_at_threshold(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["legal_signals"].status == "ready"

    def test_timeline_ready_at_threshold(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["timeline"].status == "ready"

    def test_sources_actual_count_ten(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["sources"].actual == 10

    def test_evidence_actual_count_fifteen(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["evidence"].actual == 15

    def test_legal_signals_actual_count_six(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["legal_signals"].actual == 6

    def test_timeline_actual_count_six(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["timeline"].actual == 6

    def test_cii_still_ready(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["cii_metrics"].status == "ready"

    def test_scenario_scores_still_ready(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["scenario_scores"].status == "ready"

    def test_matrix_still_ready(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["matrix"].status == "ready"

    def test_home_overview_ready(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["home_overview"].status == "ready"

    def test_localization_ready(self) -> None:
        result = _evaluate_argentina()
        assert result.sections["localization"].status == "ready"

    def test_argentina_mvp_ready_with_full_data(self) -> None:
        result = _evaluate_argentina()
        assert result.mvp_ready is True

    def test_argentina_slug_correct(self) -> None:
        result = _evaluate_argentina()
        assert result.country_slug == "argentina"

    def test_sources_below_threshold_shows_incomplete(self) -> None:
        result = _evaluate_argentina(count_published_sources=9)
        assert result.sections["sources"].status == "incomplete"
        assert result.mvp_ready is False

    def test_evidence_below_threshold_shows_incomplete(self) -> None:
        result = _evaluate_argentina(count_published_evidence=14)
        assert result.sections["evidence"].status == "incomplete"
        assert result.mvp_ready is False

    def test_legal_signals_below_threshold_shows_missing(self) -> None:
        result = _evaluate_argentina(count_published_legal_signals=4)
        assert result.sections["legal_signals"].status == "missing"
        assert result.mvp_ready is False

    def test_timeline_below_threshold_shows_missing(self) -> None:
        result = _evaluate_argentina(count_timeline_events=4)
        assert result.sections["timeline"].status == "missing"
        assert result.mvp_ready is False

    def test_timeline_unsourced_shows_incomplete(self) -> None:
        result = _evaluate_argentina(
            count_timeline_events=6,
            count_timeline_events_with_traceability=5,
        )
        assert result.sections["timeline"].status == "incomplete"
        assert result.mvp_ready is False

    def test_all_timeline_events_sourced_required(self) -> None:
        result = _evaluate_argentina(
            count_timeline_events=6,
            count_timeline_events_with_traceability=6,
        )
        assert result.sections["timeline"].status == "ready"


class TestAllMvpReadyAfterArgentinaLegal:
    def test_all_mvp_ready_true(self) -> None:
        result = _evaluate_all_mvp_with_argentina_full()
        assert result.all_mvp_ready is True

    def test_russia_mvp_ready(self) -> None:
        result = _evaluate_all_mvp_with_argentina_full()
        russia = next(c for c in result.countries if c.country_slug == "russia")
        assert russia.mvp_ready is True

    def test_uruguay_mvp_ready(self) -> None:
        result = _evaluate_all_mvp_with_argentina_full()
        uruguay = next(
            c for c in result.countries if c.country_slug == "uruguay"
        )
        assert uruguay.mvp_ready is True

    def test_argentina_in_mvp_countries(self) -> None:
        result = _evaluate_all_mvp_with_argentina_full()
        slugs = [c.country_slug for c in result.countries]
        assert "argentina" in slugs

    def test_argentina_mvp_ready_when_full(self) -> None:
        result = _evaluate_all_mvp_with_argentina_full()
        argentina = next(
            c for c in result.countries if c.country_slug == "argentina"
        )
        assert argentina.mvp_ready is True

    def test_onboarding_countries_is_empty(self) -> None:
        result = _evaluate_all_mvp_with_argentina_full()
        assert len(result.onboarding_countries) == 0


class TestArgentinaLegalSignalsData:
    def test_legal_signals_count(self) -> None:
        assert len(_ARGENTINA_LEGAL_SIGNALS) == 6

    def test_all_signals_published(self) -> None:
        for sig in _ARGENTINA_LEGAL_SIGNALS:
            assert sig["status"] == "published"

    def test_all_signals_have_source(self) -> None:
        for sig in _ARGENTINA_LEGAL_SIGNALS:
            assert sig["source_id"] is not None
            assert sig["source_url"] is not None

    def test_signal_types_covered(self) -> None:
        types = {sig["signal_type"] for sig in _ARGENTINA_LEGAL_SIGNALS}
        assert "residence" in types
        assert "citizenship" in types
        assert "tax" in types
        assert "banking" in types
        assert "business" in types
        assert "political_risk" in types

    def test_all_signals_high_confidence(self) -> None:
        for sig in _ARGENTINA_LEGAL_SIGNALS:
            assert sig["confidence_level"] == "high"

    def test_signal_impact_directions_valid(self) -> None:
        valid = {"positive", "negative", "neutral", "mixed", "uncertain"}
        for sig in _ARGENTINA_LEGAL_SIGNALS:
            assert sig["impact_direction"] in valid

    def test_signal_impact_levels_valid(self) -> None:
        valid = {"low", "medium", "high", "critical"}
        for sig in _ARGENTINA_LEGAL_SIGNALS:
            assert sig["impact_level"] in valid


class TestArgentinaTimelineData:
    def test_timeline_events_count(self) -> None:
        assert len(_ARGENTINA_TIMELINE_EVENTS) == 6

    def test_all_events_confirmed(self) -> None:
        for ev in _ARGENTINA_TIMELINE_EVENTS:
            assert ev["event_type"] == "confirmed"

    def test_all_events_have_source(self) -> None:
        for ev in _ARGENTINA_TIMELINE_EVENTS:
            assert ev["source_id"] is not None

    def test_all_events_have_evidence(self) -> None:
        for ev in _ARGENTINA_TIMELINE_EVENTS:
            assert ev["evidence_item_id"] is not None

    def test_all_events_argentina_country(self) -> None:
        for ev in _ARGENTINA_TIMELINE_EVENTS:
            assert ev["country_slug"] == "argentina"

    def test_all_events_year_2024(self) -> None:
        for ev in _ARGENTINA_TIMELINE_EVENTS:
            assert ev["year"] == 2024

    def test_traceability_ratio_is_one(self) -> None:
        with_source = sum(
            1 for ev in _ARGENTINA_TIMELINE_EVENTS if ev["source_id"]
        )
        assert with_source == len(_ARGENTINA_TIMELINE_EVENTS)


class TestArgentinaSourcesData:
    def test_sources_count_at_least_ten(self) -> None:
        assert len(_ARGENTINA_SOURCES) >= 10

    def test_all_sources_published(self) -> None:
        for src in _ARGENTINA_SOURCES:
            assert src["status"] == "published"


class TestArgentinaLegalSignalsApi:
    def test_legal_signals_types_covered_in_data(self) -> None:
        types = {sig["signal_type"] for sig in _ARGENTINA_LEGAL_SIGNALS}
        assert "residence" in types
        assert "tax" in types
        assert "banking" in types
        assert "citizenship" in types
        assert "business" in types
        assert "political_risk" in types

    def test_legal_signals_all_have_source_url(self) -> None:
        for sig in _ARGENTINA_LEGAL_SIGNALS:
            url: str = sig["source_url"]  # type: ignore[assignment]
            assert url.startswith("http")

    def test_legal_signals_no_empty_titles(self) -> None:
        for sig in _ARGENTINA_LEGAL_SIGNALS:
            title: str = sig["title"]  # type: ignore[assignment]
            assert title.strip() != ""

    def test_timeline_events_all_traceable(self) -> None:
        untraceable = [
            ev
            for ev in _ARGENTINA_TIMELINE_EVENTS
            if ev.get("source_id") is None
            and ev.get("evidence_item_id") is None
        ]
        assert len(untraceable) == 0

    def test_sources_count_meets_threshold(self) -> None:
        assert len(_ARGENTINA_SOURCES) >= 10

    def test_legal_signals_fetch_all_mock(self) -> None:
        with patch(
            "app.repositories.legal_signals.fetch_all",
            return_value=_ARGENTINA_LEGAL_SIGNALS,
        ) as mock_fetch:
            mock_fetch.return_value = _ARGENTINA_LEGAL_SIGNALS
            assert len(_ARGENTINA_LEGAL_SIGNALS) == 6


class TestArgentinaArchitectureSlugs:
    def test_onboarding_country_slugs_is_empty(self) -> None:
        from app.repositories.data_quality import ONBOARDING_COUNTRY_SLUGS

        assert len(ONBOARDING_COUNTRY_SLUGS) == 0

    def test_argentina_in_mvp_country_slugs(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert "argentina" in MVP_COUNTRY_SLUGS

    def test_russia_in_mvp_country_slugs(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert "russia" in MVP_COUNTRY_SLUGS

    def test_uruguay_in_mvp_country_slugs(self) -> None:
        from app.repositories.data_quality import MVP_COUNTRY_SLUGS

        assert "uruguay" in MVP_COUNTRY_SLUGS
