from app.core.locales import SOURCE_LOCALE
from app.repositories import decision_engine as repository
from app.repositories.cii import (
    get_active_cii_metric_definitions as get_active_cii_metric_definitions,
    get_cii_metric_values_for_countries as get_cii_metric_values_for_countries,
)
from app.repositories.common import build_locale
from app.schemas.common import LocaleCode, LocaleResolution
from app.schemas.decision_engine import DecisionCountryRef, DecisionCountryScore
from app.services.localization import (
    overlay_localized_fields as overlay_localized_fields,
)
from app.services.methodology_config import (
    ConfidenceThresholds,
    ScoreLabelThresholds,
)
from app.services.persona_weights import (
    build_persona_weight_profile as build_persona_weight_profile,
)
from app.services.score_labels import score_label
from collections.abc import Iterable
from psycopg import Connection
from typing import Any, Literal, cast


ScoreLabel = Literal["weak", "limited", "moderate", "strong", "excellent"]


CAVEAT = (
    "This MVP decision output is not legal, tax, immigration, investment, or safety advice. "
    "Use it as a structured question list and verify every claim with qualified experts."
)
CAVEAT_RU = (
    "Этот MVP-результат не является юридической, налоговой, миграционной, "
    "инвестиционной или консультацией по безопасности. Используйте его как "
    "структурированный список вопросов и проверяйте каждый вывод с экспертами."
)


def _locale(
    rows: list[dict[str, Any]], requested_locale: str
) -> LocaleResolution:
    return build_locale(rows, requested_locale)


def get_score_label(score: float, thresholds: ScoreLabelThresholds) -> str:
    return score_label(score, thresholds)


def _score_label_literal(
    score: float, thresholds: ScoreLabelThresholds
) -> ScoreLabel:
    return cast(ScoreLabel, get_score_label(score, thresholds))


def aggregate_confidence(
    values: Iterable[str | None], thresholds: ConfidenceThresholds
) -> str:
    confidence_value = {"low": 1, "medium": 2, "high": 3}
    clean_values = [
        confidence_value[value] for value in values if value in confidence_value
    ]
    if not clean_values:
        return "low"
    average = sum(clean_values) / len(clean_values)
    if average >= thresholds.high_min_average:
        return "high"
    if average >= thresholds.medium_min_average:
        return "medium"
    return "low"


def _country_ref(country: dict[str, Any]) -> DecisionCountryRef:
    return DecisionCountryRef(
        id=str(country["id"]),
        slug=country["slug"],
        name=country["name"],
        iso_code=country.get("iso_code"),
    )


def _source_ids(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    return []


def _collect_source_ids(
    breakdowns: list[dict[str, Any]], legal_signals: list[dict[str, Any]]
) -> list[str]:
    source_ids = [
        source_id
        for breakdown in breakdowns
        for source_id in _source_ids(breakdown.get("source_ids"))
    ]
    source_ids.extend(
        str(signal["source_id"])
        for signal in legal_signals
        if signal.get("source_id")
    )
    return sorted(set(source_ids))


def _group_by(
    rows: list[dict[str, Any]], key: str
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    return grouped


def _caveat(locale: str) -> str:
    if locale == LocaleCode.ru:
        return CAVEAT_RU
    return CAVEAT


def _localized_explanation(
    explanation_en: str | None, explanation_ru: str | None, locale: str
) -> str:
    if locale == LocaleCode.ru and explanation_ru:
        return explanation_ru
    return explanation_en or explanation_ru or ""


def _field_translation_status(
    value_en: str | None, value_ru: str | None, locale: str
) -> str:
    if locale == SOURCE_LOCALE and value_en:
        return "source"
    if locale == LocaleCode.ru and value_ru:
        return "translated"
    if value_en:
        return "fallback"
    return "missing"


def _attach_breakdowns_and_sources(
    connection: Connection[Any], rows: list[dict[str, Any]], locale: str
) -> list[DecisionCountryScore]:
    score_ids = [str(row["id"]) for row in rows]
    breakdown_rows = repository.list_score_breakdowns(connection, score_ids)
    source_rows = repository.list_score_sources(
        connection, sorted({row["country_slug"] for row in rows})
    )
    breakdowns_by_score: dict[str, list[dict[str, Any]]] = {}
    for breakdown in breakdown_rows:
        breakdown["explanation"] = _localized_explanation(
            breakdown.get("explanation_en"),
            breakdown.get("explanation_ru"),
            locale,
        )
        breakdown["translation_status"] = _field_translation_status(
            breakdown.get("explanation_en"),
            breakdown.get("explanation_ru"),
            locale,
        )
        breakdowns_by_score.setdefault(
            str(breakdown["country_score_id"]), []
        ).append(breakdown)
    sources_by_country: dict[str, list[dict[str, Any]]] = {}
    for source in source_rows:
        for row in rows:
            if source["country_id"] == row["country_id"]:
                sources_by_country.setdefault(row["country_slug"], []).append(
                    source
                )
    return [
        DecisionCountryScore(
            **row,
            breakdowns=breakdowns_by_score.get(str(row["id"]), []),
            source_references=sources_by_country.get(row["country_slug"], [])[
                :5
            ],
        )
        for row in rows
    ]
