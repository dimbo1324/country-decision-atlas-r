from app.core.locales import SOURCE_LOCALE, SupportedLocale
from app.repositories.cii import get_country_cii
from app.repositories.country_read_model import (
    get_country_read_model_country,
    get_country_read_model_evidence_summary,
    get_country_read_model_profile,
    get_country_read_model_user_stories_summary,
    list_country_read_model_legal_signals,
    list_country_read_model_score_breakdowns,
    list_country_read_model_scores,
    list_country_read_model_sources,
)
from app.schemas.common import (
    LocaleResolution,
    TranslationStatus,
    locale_resolution,
)
from app.schemas.country_read_model import (
    CountryReadModelCii,
    CountryReadModelCiiMetric,
    CountryReadModelMeta,
    CountryReadModelResponse,
)
from app.services.cache import cache_ttl, get_cache_backend
from app.services.cache_keys import country_card_key
from app.services.cii import compute_confidence
from app.services.localization import overlay_localized_fields
from app.services.persona_runtime import (
    aggregate_persona_cii_score,
    persona_metric_weight_metadata,
)
from datetime import UTC, date, datetime, time
from psycopg import Connection
from typing import Any


LEGAL_SIGNAL_LIMIT = 5
SOURCE_LIMIT = 10


def get_country_read_model(
    connection: Connection[Any],
    country_slug: str,
    locale: SupportedLocale,
) -> CountryReadModelResponse | None:
    key = country_card_key(country_slug, locale)
    cache = get_cache_backend()
    cached = cache.get_json(key)
    if cached is not None:
        return CountryReadModelResponse.model_validate(cached)
    result = _get_country_read_model_uncached(connection, country_slug, locale)
    if result is not None:
        cache.set_json(key, result.model_dump(mode="json"), cache_ttl())
    return result


def _get_country_read_model_uncached(
    connection: Connection[Any],
    country_slug: str,
    locale: SupportedLocale,
) -> CountryReadModelResponse | None:
    country = get_country_read_model_country(connection, country_slug, locale)
    if country is None:
        return None
    profile = get_country_read_model_profile(connection, country_slug, locale)
    if profile is not None:
        profile_items = overlay_localized_fields(
            connection,
            [profile],
            "country_card",
            "id",
            [
                ("executive_summary", "executive_summary", None, None),
                ("migration_overview", "migration_overview", None, None),
                ("tax_overview", "tax_overview", None, None),
                (
                    "cost_of_living_overview",
                    "cost_of_living_overview",
                    None,
                    None,
                ),
                ("business_overview", "business_overview", None, None),
                ("safety_overview", "safety_overview", None, None),
                ("legal_signals_summary", "legal_signals_summary", None, None),
                ("risk_summary", "risk_summary", None, None),
                ("source_summary", "source_summary", None, None),
            ],
            locale,
        )
        profile = profile_items[0]
    scores = list_country_read_model_scores(connection, country_slug)
    scores = overlay_localized_fields(
        connection,
        scores,
        "scenario",
        "scenario_id",
        [("title", "scenario_title", "title_ru", "title_en")],
        locale,
    )
    scores = overlay_localized_fields(
        connection,
        scores,
        "country_score",
        "id",
        [("explanation", "explanation", "explanation_ru", "explanation_en")],
        locale,
    )
    score_ids = [score["id"] for score in scores]
    breakdowns = list_country_read_model_score_breakdowns(connection, score_ids)
    breakdowns = overlay_localized_fields(
        connection,
        breakdowns,
        "country_score_breakdown",
        "id",
        [("explanation", "explanation", "explanation_ru", "explanation_en")],
        locale,
    )
    breakdowns_by_score_id = group_breakdowns_by_score_id(breakdowns)
    for score in scores:
        score["breakdowns"] = breakdowns_by_score_id.get(score["id"], [])
    legal_signals = list_country_read_model_legal_signals(
        connection, country_slug, LEGAL_SIGNAL_LIMIT
    )
    legal_signals = overlay_localized_fields(
        connection,
        legal_signals,
        "legal_signal",
        "id",
        [
            ("title", "title", "title_ru", "title_en"),
            ("summary", "summary", "summary_ru", "summary_en"),
        ],
        locale,
    )
    sources = list_country_read_model_sources(
        connection, country_slug, SOURCE_LIMIT
    )
    evidence_summary = get_country_read_model_evidence_summary(
        connection, country_slug
    )
    user_stories_summary = get_country_read_model_user_stories_summary(
        connection, country_slug
    )
    cii = build_cii(get_country_cii(connection, country_slug))
    localized_blocks = [
        country,
        profile,
        *scores,
        *breakdowns,
        *legal_signals,
    ]
    return CountryReadModelResponse(
        country=country,
        profile=profile,
        scores=scores,
        legal_signals=legal_signals,
        sources=sources,
        evidence_summary=evidence_summary,
        user_stories_summary=user_stories_summary,
        cii=cii,
        meta=CountryReadModelMeta(
            scores_count=len(scores),
            legal_signals_count=len(legal_signals),
            sources_count=len(sources),
            last_updated_at=calculate_last_updated_at(
                country,
                profile,
                scores,
                legal_signals,
                sources,
            ),
        ),
        locale=resolve_read_model_locale(locale, localized_blocks),
    )


def group_breakdowns_by_score_id(
    breakdowns: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for breakdown in breakdowns:
        grouped.setdefault(str(breakdown["country_score_id"]), []).append(
            breakdown
        )
    return grouped


def resolve_read_model_locale(
    requested_locale: SupportedLocale,
    localized_blocks: list[dict[str, Any] | None],
) -> LocaleResolution:
    if requested_locale == SOURCE_LOCALE:
        return locale_resolution(
            requested_locale, SOURCE_LOCALE, TranslationStatus.source
        )
    existing_blocks = [block for block in localized_blocks if block is not None]
    if not existing_blocks:
        return locale_resolution(
            requested_locale, SOURCE_LOCALE, TranslationStatus.missing
        )
    statuses = {
        block.get("translation_status")
        for block in existing_blocks
        if block.get("translation_status")
    }
    if statuses == {TranslationStatus.translated.value}:
        return locale_resolution(
            requested_locale, requested_locale, TranslationStatus.translated
        )
    if TranslationStatus.fallback.value in statuses:
        return locale_resolution(
            requested_locale, SOURCE_LOCALE, TranslationStatus.fallback
        )
    if TranslationStatus.missing.value in statuses:
        return locale_resolution(
            requested_locale, SOURCE_LOCALE, TranslationStatus.missing
        )
    return locale_resolution(
        requested_locale, SOURCE_LOCALE, TranslationStatus.fallback
    )


def calculate_last_updated_at(
    *blocks: dict[str, Any] | list[dict[str, Any]] | None,
) -> datetime | None:
    values: list[datetime] = []
    for block in blocks:
        rows = block if isinstance(block, list) else [block]
        for row in rows:
            if row is None:
                continue
            for key in (
                "updated_at",
                "calculated_at",
                "last_checked_at",
                "published_at",
                "published_date",
            ):
                value = row.get(key)
                normalized = normalize_datetime(value)
                if normalized is not None:
                    values.append(normalized)
    if not values:
        return None
    return max(values)


def normalize_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min, tzinfo=UTC)
    return None


def build_cii(row: dict[str, Any] | None) -> CountryReadModelCii | None:
    if row is None:
        return None
    raw_metrics = row.get("metrics") or []
    metrics = [CountryReadModelCiiMetric.model_validate(m) for m in raw_metrics]
    return CountryReadModelCii(
        overall_score=float(row["overall_score"]),
        confidence=str(row["confidence"]),
        drift=float(row["drift"]) if row.get("drift") is not None else None,
        version=str(row["version"]),
        formula_version=row.get("formula_version"),
        aggregation_method=row.get("aggregation_method"),
        quality_warnings=[],
        calculated_at=row["calculated_at"],
        metrics=metrics,
    )


def build_persona_adjusted_cii(
    row: dict[str, Any] | None,
    profile: dict[str, Any],
    metric_defs: list[dict[str, Any]],
) -> CountryReadModelCii | None:
    if row is None:
        return None
    raw_metrics = row.get("metrics") or []
    metric_defs_by_slug = {str(item["slug"]): item for item in metric_defs}
    aggregate = aggregate_persona_cii_score(
        raw_metrics, profile, metric_defs_by_slug
    )
    metric_entries = []
    for metric in raw_metrics:
        metric_slug = str(metric["slug"])
        weight_metadata = persona_metric_weight_metadata(metric_slug, profile)
        if weight_metadata is None:
            metric_entries.append(metric)
            continue
        score = float(metric["score"])
        metric_entries.append(
            {
                **metric,
                "weight": weight_metadata["adjusted_weight"],
                "weighted_score": round(
                    score * weight_metadata["adjusted_weight"], 4
                ),
                **weight_metadata,
            }
        )
    return CountryReadModelCii(
        overall_score=float(aggregate["overall_score"]),
        confidence=compute_confidence(
            [
                {
                    "reliability": metric.get("reliability", "medium"),
                    "normalized_value": metric.get("score"),
                }
                for metric in raw_metrics
            ]
        ),
        drift=float(row["drift"]) if row.get("drift") is not None else None,
        version=str(row["version"]),
        formula_version=aggregate.get("formula_version")
        or row.get("formula_version"),
        aggregation_method=aggregate.get("aggregation_method")
        or row.get("aggregation_method"),
        quality_warnings=list(aggregate.get("warnings") or []),
        calculated_at=row["calculated_at"],
        metrics=[
            CountryReadModelCiiMetric.model_validate(m) for m in metric_entries
        ],
        applied_persona=profile["persona"],
        persona_weight_profile=profile,
    )
