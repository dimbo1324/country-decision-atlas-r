from app.api.v1 import countries as countries_route
from app.core.locales import get_locale
from app.schemas.common import locale_resolution
from app.schemas.country_read_model import (
    CountryReadModelMeta,
    CountryReadModelResponse,
)
from app.services import country_read_model
import asyncio
from datetime import UTC, datetime
from fastapi import HTTPException
from psycopg import Connection
from tests.test_openapi_contract import load_contract
from typing import Any, cast


NOW = datetime.now(UTC)
CONNECTION = cast(Connection[Any], object())


def sample_response(slug: str, locale: str) -> CountryReadModelResponse:
    status = "source" if locale == "en" else "translated"
    return CountryReadModelResponse(
        country={
            "id": "country-id",
            "slug": slug,
            "iso_code": "UY" if slug == "uruguay" else "RU",
            "name": "Uruguay" if slug == "uruguay" else "Russia",
            "region": "Americas" if slug == "uruguay" else "Europe",
            "status": "published",
        },
        profile={
            "executive_summary": "Summary",
            "migration_overview": "Migration",
            "tax_overview": "Tax",
            "cost_of_living_overview": "Cost",
            "business_overview": "Business",
            "safety_overview": "Safety",
            "legal_signals_summary": "Signals",
            "risk_summary": "Risk",
            "source_summary": "Sources",
        },
        scores=[
            {
                "id": f"score-{index}",
                "scenario_slug": f"scenario-{index}",
                "scenario_title": f"Scenario {index}",
                "score": 70.0 + index,
                "confidence": "medium",
                "explanation": "Explanation",
                "calculated_at": NOW,
                "breakdowns": [
                    {
                        "criterion": "legalization_score",
                        "score": 70.0,
                        "weight": 0.25,
                        "weighted_score": 17.5,
                        "explanation": "Breakdown",
                        "confidence": "medium",
                        "source_ids": ["source-id"],
                    }
                ],
            }
            for index in range(5)
        ],
        legal_signals=[
            {
                "id": "signal-id",
                "title": "Signal",
                "summary": "Summary",
                "signal_type": "residence",
                "impact_direction": "positive",
                "impact_level": "medium",
                "affected_groups": ["relocators"],
                "published_date": NOW.date(),
                "effective_date": NOW.date(),
                "confidence": "medium",
            }
        ],
        sources=[
            {
                "id": "source-id",
                "title": "Source",
                "url": "https://example.invalid/source",
                "source_type": "official",
                "publisher": "Publisher",
                "confidence": "medium",
                "published_at": NOW.date(),
                "last_checked_at": NOW.date(),
            }
        ],
        evidence_summary={
            "total": 2,
            "high_confidence": 1,
            "medium_confidence": 1,
            "low_confidence": 0,
        },
        user_stories_summary={
            "total": 1,
            "synthetic": 1,
            "average_satisfaction_score": 7.5,
        },
        meta=CountryReadModelMeta(
            scores_count=5,
            legal_signals_count=1,
            sources_count=1,
            last_updated_at=NOW,
        ),
        locale=locale_resolution(locale, locale if locale == "ru" else "en", status),
    )


def test_country_read_model_route_default_locale(monkeypatch: Any) -> None:
    def fake_get_country_read_model(
        _: Connection[Any], country_slug: str, locale: str
    ) -> CountryReadModelResponse:
        return sample_response(country_slug, locale)

    monkeypatch.setattr(
        countries_route,
        "get_country_read_model",
        fake_get_country_read_model,
    )
    result = asyncio.run(
        countries_route.read_country_card("uruguay", CONNECTION, get_locale())
    )
    body = result.model_dump(mode="json")

    assert set(body) == {
        "country",
        "profile",
        "scores",
        "legal_signals",
        "sources",
        "evidence_summary",
        "user_stories_summary",
        "meta",
        "locale",
    }
    assert body["country"]["slug"] == "uruguay"
    assert body["profile"]["executive_summary"] == "Summary"
    assert body["locale"]["requested_locale"] == "en"
    assert body["locale"]["resolved_locale"] == "en"
    assert body["locale"]["translation_status"] == "source"
    assert len(body["scores"]) >= 5
    assert body["scores"][0]["breakdowns"]
    assert len(body["legal_signals"]) <= 5
    assert len(body["sources"]) <= 10
    assert body["meta"]["scores_count"] == len(body["scores"])
    assert body["meta"]["legal_signals_count"] == len(body["legal_signals"])
    assert body["meta"]["sources_count"] == len(body["sources"])
    assert body["evidence_summary"]["total"] == 2
    assert body["user_stories_summary"]["synthetic"] == 1


def test_country_read_model_route_supported_slugs_and_locales(
    monkeypatch: Any,
) -> None:
    def fake_get_country_read_model(
        _: Connection[Any], country_slug: str, locale: str
    ) -> CountryReadModelResponse:
        return sample_response(country_slug, locale)

    monkeypatch.setattr(
        countries_route,
        "get_country_read_model",
        fake_get_country_read_model,
    )
    for slug in ("russia", "uruguay"):
        for locale in ("en", "ru"):
            result = asyncio.run(
                countries_route.read_country_card(slug, CONNECTION, get_locale(locale))
            )
            body = result.model_dump(mode="json")

            assert body["country"]["slug"] == slug
            assert body["locale"]["requested_locale"] == locale
            assert body["locale"]["translation_status"] in {
                "source",
                "translated",
                "fallback",
            }


def test_country_read_model_route_unknown_country(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        countries_route,
        "get_country_read_model",
        lambda *_: None,
    )
    try:
        asyncio.run(
            countries_route.read_country_card("unknown", CONNECTION, get_locale("en"))
        )
    except HTTPException as error:
        details = cast(dict[str, Any], error.detail)

        assert error.status_code == 404
        assert details["error"]["code"] == "country_not_found"
    else:
        raise AssertionError("Unknown country was accepted")


def test_country_read_model_route_unsupported_locale() -> None:
    try:
        get_locale("es")
    except HTTPException as error:
        details = cast(dict[str, Any], error.detail)

        assert error.status_code == 422
        assert details["error"]["code"] == "unsupported_locale"
    else:
        raise AssertionError("Unsupported locale was accepted")


def test_country_read_model_service_aggregates_blocks(monkeypatch: Any) -> None:
    country = {
        "id": "country-id",
        "slug": "uruguay",
        "iso_code": "UY",
        "name": "Uruguay",
        "region": "Americas",
        "status": "published",
        "updated_at": NOW,
        "resolved_locale": "ru",
        "translation_status": "translated",
    }
    profile = {
        "executive_summary": "Summary",
        "updated_at": NOW,
        "resolved_locale": "en",
        "translation_status": "fallback",
    }
    scores = [
        {
            "id": "score-id",
            "scenario_slug": "relocation_residence",
            "scenario_title": "Relocation",
            "score": 72.0,
            "confidence": "medium",
            "explanation": "Explanation",
            "calculated_at": NOW,
            "updated_at": NOW,
            "resolved_locale": "ru",
            "translation_status": "translated",
        }
    ]
    breakdowns = [
        {
            "country_score_id": "score-id",
            "criterion": "legalization_score",
            "score": 72.0,
            "weight": 0.25,
            "weighted_score": 18.0,
            "explanation": "Breakdown",
            "source_ids": [],
            "confidence": "medium",
            "updated_at": NOW,
            "resolved_locale": "ru",
            "translation_status": "translated",
        }
    ]
    legal_signals = [
        {
            "id": "signal-id",
            "title": "Signal",
            "summary": "Summary",
            "signal_type": "residence",
            "impact_direction": "positive",
            "impact_level": "medium",
            "affected_groups": [],
            "published_date": NOW.date(),
            "effective_date": NOW.date(),
            "confidence": "medium",
            "updated_at": NOW,
            "resolved_locale": "ru",
            "translation_status": "translated",
        }
    ]
    sources = [
        {
            "id": "source-id",
            "title": "Source",
            "url": "https://example.invalid/source",
            "source_type": "official",
            "publisher": "Publisher",
            "confidence": "medium",
            "published_at": NOW.date(),
            "last_checked_at": NOW.date(),
            "updated_at": NOW,
        }
    ]
    evidence_summary = {
        "total": 2,
        "high_confidence": 1,
        "medium_confidence": 1,
        "low_confidence": 0,
    }
    user_stories_summary = {
        "total": 1,
        "synthetic": 1,
        "average_satisfaction_score": 7.5,
    }

    monkeypatch.setattr(
        country_read_model,
        "overlay_localized_fields",
        lambda _conn, items, *_args, **_kw: items,
    )
    monkeypatch.setattr(
        country_read_model, "get_country_read_model_country", lambda *_: country
    )
    monkeypatch.setattr(
        country_read_model, "get_country_read_model_profile", lambda *_: profile
    )
    monkeypatch.setattr(
        country_read_model, "list_country_read_model_scores", lambda *_: scores
    )
    monkeypatch.setattr(
        country_read_model,
        "list_country_read_model_score_breakdowns",
        lambda *_: breakdowns,
    )
    monkeypatch.setattr(
        country_read_model,
        "list_country_read_model_legal_signals",
        lambda *_: legal_signals,
    )
    monkeypatch.setattr(
        country_read_model, "list_country_read_model_sources", lambda *_: sources
    )
    monkeypatch.setattr(
        country_read_model,
        "get_country_read_model_evidence_summary",
        lambda *_: evidence_summary,
    )
    monkeypatch.setattr(
        country_read_model,
        "get_country_read_model_user_stories_summary",
        lambda *_: user_stories_summary,
    )

    result = country_read_model.get_country_read_model(CONNECTION, "uruguay", "ru")

    assert result is not None
    assert result.country.slug == "uruguay"
    assert result.scores[0].breakdowns[0].criterion == "legalization_score"
    assert result.meta.scores_count == 1
    assert result.meta.legal_signals_count == 1
    assert result.meta.sources_count == 1
    assert result.evidence_summary.total == 2
    assert result.user_stories_summary.synthetic == 1
    assert result.locale.translation_status == "fallback"
    assert result.locale.resolved_locale == "en"


def test_country_read_model_openapi_contract() -> None:
    contract = load_contract()
    path = contract["paths"]["/api/v1/countries/{country_slug}/card"]["get"]
    schemas = contract["components"]["schemas"]

    assert path["responses"]["200"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/CountryReadModelResponse"
    }
    for schema_name in (
        "CountryReadModelResponse",
        "CountryReadModelCountry",
        "CountryReadModelProfile",
        "CountryReadModelScore",
        "CountryReadModelScoreBreakdown",
        "CountryReadModelLegalSignal",
        "CountryReadModelSource",
        "CountryReadModelEvidenceSummary",
        "CountryReadModelUserStoriesSummary",
        "CountryReadModelMeta",
        "LocaleResolution",
    ):
        assert schema_name in schemas
