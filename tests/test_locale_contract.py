from app.core.locales import validate_locale
from app.repositories import decision_engine as decision_repository
from app.schemas.common import locale_resolution, source_locale_resolution
from app.schemas.decision_engine import DecisionRunInput
from app.services import decision_engine
from datetime import UTC, date, datetime
from fastapi import HTTPException
from psycopg import Connection
from tests.test_openapi_contract import load_contract
from typing import Any, cast
from uuid import uuid4


NOW = datetime.now(UTC)
CONNECTION = cast(Connection[Any], object())
RU_RELOCATION = "\u0420\u0435\u043b\u043e\u043a\u0430\u0446\u0438\u044f"
RU_DESCRIPTION = "\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435"
RU_EXPLANATION = (
    "\u0420\u0443\u0441\u0441\u043a\u043e\u0435 "
    "\u043e\u0431\u044a\u044f\u0441\u043d\u0435\u043d\u0438\u0435"
)
RU_BREAKDOWN = (
    "\u0420\u0443\u0441\u0441\u043a\u0430\u044f "
    "\u0440\u0430\u0437\u0431\u0438\u0432\u043a\u0430"
)
RU_SIGNAL = (
    "\u0420\u0443\u0441\u0441\u043a\u0438\u0439 \u0441\u0438\u0433\u043d\u0430\u043b"
)
RU_SUMMARY = (
    "\u0420\u0443\u0441\u0441\u043a\u043e\u0435 \u0440\u0435\u0437\u044e\u043c\u0435"
)
RU_MVP_SCORE = "MVP-\u0431\u0430\u043b\u043b"


def card_row(status: str) -> dict[str, Any]:
    return {
        "id": uuid4(),
        "country_id": uuid4(),
        "locale": "en",
        "executive_summary": "English card",
        "migration_overview": "Migration",
        "tax_overview": "Tax",
        "cost_of_living_overview": "Cost",
        "business_overview": "Business",
        "safety_overview": "Safety",
        "legal_signals_summary": "Signals",
        "risk_summary": "Risk",
        "source_summary": "Sources",
        "status": "published",
        "created_at": NOW,
        "updated_at": NOW,
        "translation_status": status,
        "resolved_locale": "ru" if status == "translated" else "en",
        "is_translated": status == "translated",
    }


def scenario_row(status: str) -> dict[str, Any]:
    return {
        "id": uuid4(),
        "slug": "relocation_residence",
        "title": RU_RELOCATION if status == "translated" else "Relocation",
        "description": RU_DESCRIPTION if status == "translated" else "Description",
        "weights": {"legalization_score": 1.0},
        "translation_status": status,
        "resolved_locale": "ru" if status == "translated" else "en",
        "is_translated": status == "translated",
    }


def score_row(status: str) -> dict[str, Any]:
    return {
        "id": uuid4(),
        "country_id": uuid4(),
        "country_slug": "uruguay",
        "country_name": "Uruguay",
        "scenario_id": uuid4(),
        "scenario_slug": "relocation_residence",
        "scenario_name": RU_RELOCATION if status == "translated" else "Relocation",
        "score": 72.0,
        "explanation": RU_EXPLANATION
        if status == "translated"
        else "English explanation",
        "confidence": "medium",
        "calculated_at": NOW,
        "translation_status": status,
        "resolved_locale": "ru" if status == "translated" else "en",
        "is_translated": status == "translated",
    }


def breakdown_row(explanation_ru: str | None) -> dict[str, Any]:
    return {
        "id": uuid4(),
        "country_score_id": uuid4(),
        "criterion": "legalization_score",
        "score": 72.0,
        "weight": 1.0,
        "weighted_score": 72.0,
        "explanation_en": "English breakdown",
        "explanation_ru": explanation_ru or "",
        "source_ids": [],
        "confidence": "medium",
        "created_at": NOW,
        "updated_at": NOW,
    }


def legal_signal_row(status: str) -> dict[str, Any]:
    return {
        "id": uuid4(),
        "country_id": uuid4(),
        "title": RU_SIGNAL if status == "translated" else "English signal",
        "summary": RU_SUMMARY if status == "translated" else "English summary",
        "signal_type": "policy",
        "impact_direction": "neutral",
        "impact_level": "low",
        "affected_groups": [],
        "published_date": date.today(),
        "effective_date": date.today(),
        "source_id": None,
        "confidence": "medium",
        "status": "published",
        "created_at": NOW,
        "updated_at": NOW,
        "translation_status": status,
        "resolved_locale": "ru" if status == "translated" else "en",
        "is_translated": status == "translated",
    }


def test_locale_resolution_status_values() -> None:
    assert locale_resolution("en", "en", "source").translation_status == "source"
    assert (
        locale_resolution("ru", "ru", "translated").translation_status == "translated"
    )
    assert locale_resolution("ru", "en", "fallback").translation_status == "fallback"
    assert locale_resolution("ru", "en", "missing").translation_status == "missing"
    assert source_locale_resolution("ru").translation_status == "fallback"


def test_country_card_locale_fallback(monkeypatch: Any) -> None:
    def fake_get_country_card(_: Any, __: str, locale: str) -> dict[str, Any]:
        return card_row("source" if locale == "en" else "fallback")

    monkeypatch.setattr(decision_repository, "get_country_card", fake_get_country_card)

    english = decision_engine.get_country_card(CONNECTION, "russia", "en")
    russian = decision_engine.get_country_card(CONNECTION, "russia", "ru")

    assert english.locale.requested_locale == "en"
    assert english.locale.translation_status == "source"
    assert russian.locale.requested_locale == "ru"
    assert russian.locale.resolved_locale == "en"
    assert russian.locale.translation_status == "fallback"


def test_scenario_locale_metadata(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        decision_repository,
        "get_scenario",
        lambda *_: scenario_row("translated"),
    )

    row = decision_engine.get_scenario(CONNECTION, "relocation_residence", "ru")
    response_locale = decision_engine._locale([row], "ru")

    assert row["title"] == RU_RELOCATION
    assert response_locale.translation_status == "translated"


def test_legal_signal_locale_fallback(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        decision_repository,
        "get_legal_signal",
        lambda *_: legal_signal_row("fallback"),
    )

    response = decision_engine.get_legal_signal(CONNECTION, str(uuid4()), "ru")

    assert response.item.title == "English signal"
    assert response.locale.requested_locale == "ru"
    assert response.locale.resolved_locale == "en"
    assert response.locale.translation_status == "fallback"


def test_score_and_breakdown_locale(monkeypatch: Any) -> None:
    row = score_row("translated")
    row_id = str(row["id"])
    breakdown = breakdown_row(RU_BREAKDOWN)
    breakdown["country_score_id"] = row["id"]

    monkeypatch.setattr(
        decision_repository,
        "list_scenario_countries",
        lambda *_: [row],
    )
    monkeypatch.setattr(
        decision_repository,
        "list_score_breakdowns",
        lambda *_: [breakdown],
    )
    monkeypatch.setattr(decision_repository, "list_score_sources", lambda *_: [])

    scores = decision_engine.list_scenario_countries(
        CONNECTION, "relocation_residence", "ru"
    )

    assert str(scores[0].id) == row_id
    assert scores[0].explanation == RU_EXPLANATION
    assert scores[0].translation_status == "translated"
    assert scores[0].breakdowns[0].explanation == RU_BREAKDOWN
    assert scores[0].breakdowns[0].translation_status == "translated"


def test_score_breakdown_fallback(monkeypatch: Any) -> None:
    row = score_row("fallback")
    breakdown = breakdown_row(None)
    breakdown["country_score_id"] = row["id"]

    monkeypatch.setattr(
        decision_repository,
        "list_scenario_countries",
        lambda *_: [row],
    )
    monkeypatch.setattr(
        decision_repository,
        "list_score_breakdowns",
        lambda *_: [breakdown],
    )
    monkeypatch.setattr(decision_repository, "list_score_sources", lambda *_: [])

    scores = decision_engine.list_scenario_countries(
        CONNECTION, "relocation_residence", "ru"
    )

    assert scores[0].breakdowns[0].explanation == "English breakdown"
    assert scores[0].breakdowns[0].translation_status == "fallback"


def test_decision_output_respects_locale(monkeypatch: Any) -> None:
    row = score_row("translated")
    breakdown = breakdown_row(RU_BREAKDOWN)
    breakdown["country_score_id"] = row["id"]

    monkeypatch.setattr(
        decision_repository,
        "get_scenario",
        lambda *_: scenario_row("translated"),
    )
    monkeypatch.setattr(
        decision_repository,
        "list_scenario_countries",
        lambda *_: [row],
    )
    monkeypatch.setattr(
        decision_repository,
        "list_score_breakdowns",
        lambda *_: [breakdown],
    )
    monkeypatch.setattr(decision_repository, "list_score_sources", lambda *_: [])
    monkeypatch.setattr(
        decision_repository,
        "list_legal_signals",
        lambda *_: [legal_signal_row("translated")],
    )

    result = decision_engine.run_decision(
        CONNECTION,
        DecisionRunInput(
            scenario_slug="relocation_residence",
            candidate_country_slugs=["uruguay"],
            locale="ru",
        ),
    )

    assert result.locale.translation_status == "translated"
    assert RU_MVP_SCORE in result.explanation
    assert result.ranked_candidates[0].country.explanation == RU_EXPLANATION


def test_unknown_query_locale_returns_validation_error() -> None:
    try:
        validate_locale("de")
    except HTTPException as error:
        details = cast(dict[str, Any], error.detail)
        assert details["error"]["code"] == "unsupported_locale"
    else:
        raise AssertionError("Unsupported locale was accepted")


def test_unknown_decision_locale_returns_validation_error() -> None:
    try:
        decision_engine.run_decision(
            CONNECTION,
            DecisionRunInput(
                scenario_slug="relocation_residence",
                candidate_country_slugs=["uruguay"],
                locale="de",
            ),
        )
    except HTTPException as error:
        details = cast(dict[str, Any], error.detail)
        assert details["error"]["code"] == "unsupported_locale"
    else:
        raise AssertionError("Unsupported locale was accepted")


def test_openapi_locale_contract() -> None:
    schemas = load_contract()["components"]["schemas"]

    assert schemas["LocaleCode"]["enum"] == ["en", "ru"]
    assert schemas["TranslationStatus"]["enum"] == [
        "source",
        "translated",
        "fallback",
        "missing",
    ]
    assert "LocaleResolution" in schemas
