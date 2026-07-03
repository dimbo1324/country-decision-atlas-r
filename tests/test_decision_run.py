"""End-to-end decision runs across locales and core scenarios return ranked, explainable results."""

from app.api.v1 import decision as decision_route
from app.core.locales import validate_locale
from app.repositories import (
    country_pairs as country_pairs_repository,
    decision_engine as decision_repository,
)
from app.schemas.decision_engine import DecisionRunRequest
from app.services import decision_engine
from app.services.decision_engine import helpers as decision_engine_helpers
from datetime import UTC, datetime
from fastapi import HTTPException
from psycopg import Connection
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())
NOW = datetime.now(UTC)
SCENARIOS = [
    "relocation_residence",
    "permanent_residence_citizenship",
    "low_budget_living",
    "business_self_employment",
    "safety_political_risk",
]


def install_repository_fakes(monkeypatch: Any) -> None:
    def fake_scenario(_: Connection[Any], slug: str, locale: str) -> dict[str, Any]:
        status = "source" if locale == "en" else "translated"
        return {
            "slug": slug,
            "title": "Relocation"
            if locale == "en"
            else "\u041f\u0435\u0440\u0435\u0435\u0437\u0434",
            "description": "Scenario",
            "resolved_locale": locale,
            "translation_status": status,
        }

    def fake_countries(
        _: Connection[Any], slugs: list[str], locale: str
    ) -> list[dict[str, Any]]:
        status = "source" if locale == "en" else "fallback"
        return [
            {
                "id": f"{slug}-id",
                "slug": slug,
                "name": slug.title(),
                "iso_code": "UY" if slug == "uruguay" else "RU",
                "resolved_locale": "en",
                "translation_status": status,
            }
            for slug in slugs
            if slug in {"russia", "uruguay"}
        ]

    def fake_scores(
        _: Connection[Any], scenario_slug: str, slugs: list[str]
    ) -> list[dict[str, Any]]:
        scores = {"uruguay": 78.0, "russia": 42.0}
        return [
            {
                "id": f"{slug}-{scenario_slug}-score",
                "country_id": f"{slug}-id",
                "country_slug": slug,
                "scenario_slug": scenario_slug,
                "score": scores[slug],
                "score_label": "stored",
                "explanation": "Stored score",
                "explanation_ru": "Stored score",
                "explanation_en": "Stored score",
                "confidence": "high" if slug == "uruguay" else "medium",
                "calculated_at": NOW,
                "resolved_locale": "en",
                "translation_status": "source",
            }
            for slug in slugs
            if slug in scores
        ]

    def fake_breakdowns(
        _: Connection[Any], score_ids: list[str]
    ) -> list[dict[str, Any]]:
        rows = []
        for score_id in score_ids:
            is_uruguay = score_id.startswith("uruguay")
            score_values = (
                [78, 72, 56, 72, 66, 74, 78]
                if is_uruguay
                else [40, 38, 55, 34, 36, 32, 55]
            )
            for criterion, score in zip(
                [
                    "legalization_score",
                    "long_term_status_score",
                    "cost_of_living_score",
                    "safety_score",
                    "business_score",
                    "legal_stability_score",
                    "source_quality_score",
                ],
                score_values,
                strict=True,
            ):
                rows.append(
                    {
                        "country_score_id": score_id,
                        "criterion": criterion,
                        "score": float(score),
                        "weight": 0.1,
                        "weighted_score": float(score) / 10,
                        "explanation": "Breakdown",
                        "explanation_ru": "Breakdown",
                        "explanation_en": "Breakdown",
                        "source_ids": ["source-1"],
                        "confidence": "high" if is_uruguay else "medium",
                        "resolved_locale": "en",
                        "translation_status": "source",
                    }
                )
        return rows

    def fake_signals(_: Connection[Any], slugs: list[str]) -> list[dict[str, Any]]:
        return [
            {
                "id": "signal-1",
                "country_slug": slug,
                "title": "Signal",
                "title_ru": "Signal",
                "title_en": "Signal",
                "summary": "Review banking and tax constraints.",
                "summary_ru": "Review banking and tax constraints.",
                "summary_en": "Review banking and tax constraints.",
                "signal_type": "banking",
                "impact_direction": "mixed",
                "impact_level": "high",
                "source_id": "source-1",
                "confidence": "medium",
                "resolved_locale": "en",
                "translation_status": "source",
            }
            for slug in slugs
        ]

    monkeypatch.setattr(decision_repository, "get_decision_scenario", fake_scenario)
    monkeypatch.setattr(decision_repository, "list_decision_countries", fake_countries)
    monkeypatch.setattr(decision_repository, "list_decision_scores", fake_scores)
    monkeypatch.setattr(
        decision_repository, "list_decision_score_breakdowns", fake_breakdowns
    )
    monkeypatch.setattr(
        decision_repository, "list_decision_legal_signals", fake_signals
    )
    monkeypatch.setattr(
        decision_engine_helpers,
        "overlay_localized_fields",
        lambda _conn, items, *_args, **_kw: items,
    )
    monkeypatch.setattr(
        decision_repository,
        "list_decision_sources_by_ids",
        lambda *_: [
            {
                "id": "source-1",
                "title": "Source",
                "url": "https://example.invalid/source",
                "source_type": "official",
                "confidence": "high",
            }
        ],
    )
    monkeypatch.setattr(
        country_pairs_repository,
        "list_destination_compatibility",
        lambda *_: [],
    )


def payload(
    scenario_slug: str = "relocation_residence", locale: str = "en"
) -> DecisionRunRequest:
    return DecisionRunRequest(
        origin_country_slug="russia",
        candidate_country_slugs=["uruguay", "russia"],
        scenario_slug=scenario_slug,
        locale=locale,
    )


def test_decision_run_returns_ranked_explainable_results(monkeypatch: Any) -> None:
    install_repository_fakes(monkeypatch)

    result = decision_engine.run_decision(CONNECTION, payload())
    body = result.model_dump(mode="json")

    assert body["scenario"]["slug"] == "relocation_residence"
    assert body["origin_country"]["slug"] == "russia"
    assert body["meta"]["candidate_count"] == 2
    assert [item["rank"] for item in body["results"]] == [1, 2]
    assert [item["country"]["slug"] for item in body["results"]] == [
        "uruguay",
        "russia",
    ]
    for item in body["results"]:
        assert item["score_label"] in {
            "weak",
            "limited",
            "moderate",
            "strong",
            "excellent",
        }
        assert item["summary"]
        assert isinstance(item["strengths"], list)
        assert isinstance(item["weaknesses"], list)
        assert isinstance(item["risk_warnings"], list)
        assert item["confidence"] in {"low", "medium", "high"}
        assert len(item["breakdown"]) == 7
        assert item["sources"][0]["id"] == "source-1"
    assert body["results"][0]["strengths"]
    assert body["results"][1]["weaknesses"]


def test_decision_run_russian_locale_works(monkeypatch: Any) -> None:
    install_repository_fakes(monkeypatch)

    result = decision_engine.run_decision(CONNECTION, payload(locale="ru"))
    body = result.model_dump(mode="json")

    assert body["locale"]["requested_locale"] == "ru"
    assert body["locale"]["translation_status"] in {
        "source",
        "translated",
        "fallback",
        "missing",
    }
    assert body["scenario"]["title"] == "\u041f\u0435\u0440\u0435\u0435\u0437\u0434"


def test_decision_run_all_core_scenarios_work(monkeypatch: Any) -> None:
    install_repository_fakes(monkeypatch)

    for scenario_slug in SCENARIOS:
        result = decision_engine.run_decision(CONNECTION, payload(scenario_slug))
        assert result.scenario.slug == scenario_slug
        assert [item.rank for item in result.results] == [1, 2]
        assert all(item.breakdown for item in result.results)


def test_decision_run_scenario_warnings(monkeypatch: Any) -> None:
    install_repository_fakes(monkeypatch)

    business = decision_engine.run_decision(
        CONNECTION, payload("business_self_employment")
    )
    safety = decision_engine.run_decision(CONNECTION, payload("safety_political_risk"))

    assert any(
        warning.code == "banking_tax_review_required"
        for warning in business.results[0].risk_warnings
    )
    assert any(
        warning.code == "political_legal_risk_review"
        for warning in safety.results[0].risk_warnings
    )


def test_decision_run_unknown_locale_fails() -> None:
    try:
        validate_locale("es")
    except HTTPException as error:
        details = cast(dict[str, Any], error.detail)
        assert error.status_code == 422
        assert details["error"]["code"] == "unsupported_locale"
    else:
        raise AssertionError("Unsupported locale was accepted")


def test_decision_run_unknown_scenario_fails(monkeypatch: Any) -> None:
    install_repository_fakes(monkeypatch)
    monkeypatch.setattr(decision_repository, "get_decision_scenario", lambda *_: None)

    try:
        decision_engine.run_decision(CONNECTION, payload("unknown_scenario"))
    except HTTPException as error:
        assert error.status_code == 404
        assert (
            cast(dict[str, Any], error.detail)["error"]["code"] == "scenario_not_found"
        )
    else:
        raise AssertionError("Unknown scenario was accepted")


def test_decision_run_unknown_origin_country_fails(monkeypatch: Any) -> None:
    install_repository_fakes(monkeypatch)
    request = DecisionRunRequest(
        origin_country_slug="unknown",
        candidate_country_slugs=["uruguay", "russia"],
        scenario_slug="relocation_residence",
    )

    try:
        decision_engine.run_decision(CONNECTION, request)
    except HTTPException as error:
        assert error.status_code == 404
        assert (
            cast(dict[str, Any], error.detail)["error"]["code"] == "country_not_found"
        )
    else:
        raise AssertionError("Unknown country was accepted")


def test_decision_run_unknown_candidate_country_fails(monkeypatch: Any) -> None:
    install_repository_fakes(monkeypatch)
    request = DecisionRunRequest(
        origin_country_slug="russia",
        candidate_country_slugs=["uruguay", "unknown"],
        scenario_slug="relocation_residence",
    )

    try:
        decision_engine.run_decision(CONNECTION, request)
    except HTTPException as error:
        assert error.status_code == 404
        assert (
            cast(dict[str, Any], error.detail)["error"]["code"] == "country_not_found"
        )
    else:
        raise AssertionError("Unknown country was accepted")


def test_decision_run_duplicate_candidates_fail(monkeypatch: Any) -> None:
    install_repository_fakes(monkeypatch)
    request = DecisionRunRequest(
        origin_country_slug="russia",
        candidate_country_slugs=["uruguay", "uruguay"],
        scenario_slug="relocation_residence",
    )

    try:
        decision_engine.run_decision(CONNECTION, request)
    except HTTPException as error:
        assert error.status_code == 422
        assert (
            cast(dict[str, Any], error.detail)["error"]["code"]
            == "invalid_candidate_countries"
        )
    else:
        raise AssertionError("Duplicate candidates were accepted")


def test_decision_run_missing_score_fails(monkeypatch: Any) -> None:
    install_repository_fakes(monkeypatch)
    monkeypatch.setattr(
        decision_repository,
        "list_decision_scores",
        lambda *_: [
            {
                "id": "uruguay-score",
                "country_id": "uruguay-id",
                "country_slug": "uruguay",
                "scenario_slug": "relocation_residence",
                "score": 78.0,
                "score_label": "stored",
                "explanation": "Stored score",
                "confidence": "high",
                "calculated_at": NOW,
                "resolved_locale": "en",
                "translation_status": "source",
            }
        ],
    )

    try:
        decision_engine.run_decision(CONNECTION, payload())
    except HTTPException as error:
        assert error.status_code == 422
        assert (
            cast(dict[str, Any], error.detail)["error"]["code"]
            == "decision_score_not_found"
        )
    else:
        raise AssertionError("Missing score was accepted")


def test_decision_run_route_is_thin(monkeypatch: Any) -> None:
    install_repository_fakes(monkeypatch)

    result = decision_route.run_decision(payload(), CONNECTION)

    assert result.results[0].rank == 1
    assert result.results[0].country.slug == "uruguay"
