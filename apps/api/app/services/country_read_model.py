from app.core.locales import SOURCE_LOCALE, SupportedLocale
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
from app.schemas.common import LocaleResolution, TranslationStatus, locale_resolution
from app.schemas.country_read_model import (
    CountryReadModelMeta,
    CountryReadModelResponse,
)
from app.services.localization import overlay_localized_fields
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
    country = get_country_read_model_country(connection, country_slug, locale)
    if country is None:
        return None
    profile = get_country_read_model_profile(connection, country_slug, locale)
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
    sources = list_country_read_model_sources(connection, country_slug, SOURCE_LIMIT)
    evidence_summary = get_country_read_model_evidence_summary(connection, country_slug)
    user_stories_summary = get_country_read_model_user_stories_summary(
        connection, country_slug
    )
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
        grouped.setdefault(str(breakdown["country_score_id"]), []).append(breakdown)
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
