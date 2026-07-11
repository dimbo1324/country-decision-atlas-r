from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from scripts.synthetic_data.core.cii_preview import (
    CiiCountryPreview,
    generate_cii_preview,
)
from scripts.synthetic_data.core.world_models import (
    FICTIONAL_NOTICE,
    SyntheticArticle,
    SyntheticCountry,
    SyntheticSource,
    SyntheticWorld,
)
from scripts.synthetic_data.mock_server.schemas import (
    CiiCountryComparisonResponse,
    ComparedCountry,
    ComparedMetric,
    ComparedMetricValue,
    ComparedScenario,
    Country,
    CountryProfile,
    CountryReadModelCii,
    CountryReadModelCiiMetric,
    CountryTrustResponse,
    LocaleResolution,
    Source,
    TrustComponentBreakdown,
)
from typing import Literal


_SYNTHETIC_NOTES = f"{FICTIONAL_NOTICE}. Fake data from scripts/synthetic_data."


def _stable_uuid(*parts: str) -> uuid.UUID:
    return uuid.uuid5(uuid.NAMESPACE_URL, ":".join(("mock-server", *parts)))


def _confidence_label(value: int) -> str:
    if value >= 70:
        return "high"
    if value >= 40:
        return "medium"
    return "low"


def resolve_locale(requested: str | None) -> LocaleResolution:
    """Every synthetic text block is authored in English only (spec section
    8.3), so `ru` always falls back to the same `en` content -- never a
    silently invented translation."""
    requested_locale: Literal["en", "ru"] = "ru" if requested == "ru" else "en"
    status: Literal["source", "fallback"] = (
        "source" if requested_locale == "en" else "fallback"
    )
    return LocaleResolution(
        requested_locale=requested_locale,
        resolved_locale="en",
        translation_status=status,
    )


@dataclass(frozen=True)
class WorldIndex:
    """Pre-built lookups over an already-loaded `SyntheticWorld` so every
    route handler is O(1) instead of re-scanning the world's lists on every
    request."""

    world: SyntheticWorld
    generated_at: datetime
    countries_by_slug: dict[str, SyntheticCountry] = field(default_factory=dict)
    articles_by_country_id: dict[str, SyntheticArticle] = field(
        default_factory=dict
    )
    sources_by_country_id: dict[str, tuple[SyntheticSource, ...]] = field(
        default_factory=dict
    )
    cii_previews_by_slug: dict[str, CiiCountryPreview] = field(
        default_factory=dict
    )

    @staticmethod
    def build(world: SyntheticWorld) -> WorldIndex:
        generated_at = datetime.fromisoformat(
            f"{world.metadata.generated_on}T00:00:00+00:00"
        )
        countries_by_slug = {
            country.slug: country for country in world.countries
        }
        articles_by_country_id = {
            article.country_id: article for article in world.articles
        }
        sources_by_country_id = {
            country.country_id: country.sources for country in world.countries
        }
        previews = generate_cii_preview(world, seed=world.metadata.seed)
        cii_previews_by_slug = {
            preview.country_slug: preview for preview in previews
        }
        return WorldIndex(
            world=world,
            generated_at=generated_at,
            countries_by_slug=countries_by_slug,
            articles_by_country_id=articles_by_country_id,
            sources_by_country_id=sources_by_country_id,
            cii_previews_by_slug=cii_previews_by_slug,
        )


def country_to_schema(
    country: SyntheticCountry, *, generated_at: datetime
) -> Country:
    return Country(
        id=uuid.UUID(country.country_id),
        slug=country.slug,
        iso2=country.slug[:2].upper(),
        iso3=country.slug[:3].upper(),
        name=country.name,
        is_active=True,
        created_at=generated_at,
        updated_at=generated_at,
    )


def country_profile_to_schema(
    country: SyntheticCountry,
    article: SyntheticArticle | None,
    *,
    generated_at: datetime,
) -> CountryProfile:
    risk_overview = (
        f"Risks: {', '.join(country.risks)}." if country.risks else None
    )
    quality_of_life_overview = (
        f"Strengths: {', '.join(country.strengths)}."
        if country.strengths
        else None
    )
    return CountryProfile(
        id=_stable_uuid("profile", country.country_id),
        country_id=uuid.UUID(country.country_id),
        summary=article.summary if article else _SYNTHETIC_NOTES,
        risk_overview=risk_overview,
        quality_of_life_overview=quality_of_life_overview,
        created_at=generated_at,
        updated_at=generated_at,
    )


def trust_to_schema(
    country: SyntheticCountry,
    *,
    legal_signal_count: int,
    generated_at: datetime,
) -> CountryTrustResponse:
    data_confidence = country.current_metrics["data_confidence"]
    confidence = _confidence_label(data_confidence)
    trust_label = {
        "high": "Strong synthetic trust signal",
        "medium": "Moderate synthetic trust signal",
        "low": "Limited synthetic trust signal",
    }[confidence]
    return CountryTrustResponse(
        country_slug=country.slug,
        trust_score=float(data_confidence),
        trust_label=trust_label,
        confidence=confidence,
        freshness_status="synthetic",
        source_count=len(country.sources),
        evidence_count=0,
        legal_signal_count=legal_signal_count,
        route_count=0,
        platform_metric_count=0,
        components=TrustComponentBreakdown(
            source_quality_score=float(data_confidence),
        ),
        computed_at=generated_at,
        methodology_version="syn-trust-preview-v1",
        disclaimer=(
            f"{_SYNTHETIC_NOTES} This is a fake trust indicator for local "
            "development, not a real data-quality signal."
        ),
    )


def cii_preview_to_schema(preview: CiiCountryPreview) -> CountryReadModelCii:
    return CountryReadModelCii(
        overall_score=preview.overall_score,
        confidence=preview.confidence,
        version="v1.0-synthetic",
        formula_version=preview.formula_version,
        aggregation_method=preview.aggregation_method,
        quality_warnings=[_SYNTHETIC_NOTES],
        calculated_at=datetime.fromisoformat(
            f"{preview.generated_on}T00:00:00+00:00"
        ),
        metrics=[
            CountryReadModelCiiMetric(
                slug=score.metric_slug,
                name_en=score.metric_slug.removeprefix("syn_")
                .replace("_", " ")
                .title(),
                name_ru=score.metric_slug.removeprefix("syn_")
                .replace("_", " ")
                .title(),
                score=score.normalized_value,
                weight=score.weight,
                weighted_score=round(score.normalized_value * score.weight, 2),
                source_name="synthetic",
                base_weight=score.weight,
                adjusted_weight=score.weight,
            )
            for score in preview.metric_scores
        ],
    )


def comparison_to_schema(
    *,
    scenario_slug: str,
    preview_a: CiiCountryPreview,
    preview_b: CiiCountryPreview,
) -> CiiCountryComparisonResponse:
    scores_by_slug_a = {
        score.metric_slug: score for score in preview_a.metric_scores
    }
    scores_by_slug_b = {
        score.metric_slug: score for score in preview_b.metric_scores
    }
    metrics = []
    for index, metric_slug in enumerate(scores_by_slug_a):
        score_a = scores_by_slug_a[metric_slug]
        score_b = scores_by_slug_b[metric_slug]
        delta = round(score_a.normalized_value - score_b.normalized_value, 2)
        winner = (
            preview_a.country_slug
            if delta > 0
            else preview_b.country_slug
            if delta < 0
            else None
        )
        metrics.append(
            ComparedMetric(
                metric_slug=metric_slug,
                metric_name=metric_slug.removeprefix("syn_")
                .replace("_", " ")
                .title(),
                display_order=index,
                higher_is_better=True,
                weight=score_a.weight,
                delta=delta,
                winner_country_slug=winner,
                values=[
                    ComparedMetricValue(
                        country_slug=preview_a.country_slug,
                        value=score_a.normalized_value,
                        effective_value=score_a.normalized_value,
                    ),
                    ComparedMetricValue(
                        country_slug=preview_b.country_slug,
                        value=score_b.normalized_value,
                        effective_value=score_b.normalized_value,
                    ),
                ],
            )
        )
    return CiiCountryComparisonResponse(
        scenario=ComparedScenario(
            slug=scenario_slug,
            title=scenario_slug.replace("_", " ").title(),
        ),
        locale=resolve_locale(None),
        countries=[
            ComparedCountry(
                slug=preview.country_slug,
                name=preview.country_name,
                cii_score=preview.overall_score,
                cii_confidence=preview.confidence,
            )
            for preview in (preview_a, preview_b)
        ],
        metrics=metrics,
        formula_version=preview_a.formula_version,
        aggregation_method=preview_a.aggregation_method,
        quality_warnings=[_SYNTHETIC_NOTES],
    )


def source_to_schema(
    source: SyntheticSource, *, generated_at: datetime
) -> Source:
    confidence_label = _confidence_label(source.confidence)
    return Source(
        id=_stable_uuid("source", source.source_id),
        title=source.title,
        url=source.url,
        source_type="synthetic",
        country_id=uuid.UUID(source.country_id),
        reliability_level=confidence_label,
        confidence=confidence_label,
        status="published",
        notes=_SYNTHETIC_NOTES,
        created_at=generated_at,
        updated_at=generated_at,
    )
