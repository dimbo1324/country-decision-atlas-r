from app.core.config import Settings
from app.core.locales import validate_locale
from app.repositories import ai_context as repository
from app.schemas.ai import AICitation, AIContextItem
from dataclasses import dataclass
from psycopg import Connection
from typing import Any


REFUSAL_RU = "Недостаточно опубликованных данных, чтобы ответить надёжно."
REFUSAL_EN = "There is not enough published data to answer reliably."
DISCLAIMER_RU = (
    "Это не юридическая консультация. Ответ основан только на опубликованных "
    "данных проекта и указанных источниках."
)
DISCLAIMER_EN = (
    "This is not legal advice. The answer is based only on published project "
    "data and cited sources."
)


@dataclass(frozen=True)
class AIContextPackage:
    system_rules: list[str]
    user_question: str
    grounded_context: list[AIContextItem]
    citations: list[AICitation]
    citation_policy: str
    disclaimer_policy: str
    locale: str
    refusal_reason: str | None


def disclaimer(locale: str) -> str:
    return DISCLAIMER_RU if locale == "ru" else DISCLAIMER_EN


def refusal_reason(locale: str) -> str:
    return REFUSAL_RU if locale == "ru" else REFUSAL_EN


def build_ask_context(
    connection: Connection[Any],
    settings: Settings,
    *,
    question: str,
    locale: str,
    types: list[str] | None,
    country_slug: str | None,
    route_id: str | None,
    route_slug: str | None,
) -> AIContextPackage:
    resolved_locale = validate_locale(locale)
    normalized_query = _normalize_query(question)
    rows: list[dict[str, Any]] = []
    if route_id or route_slug:
        rows.extend(
            repository.get_route_ai_context(
                connection,
                route_id=route_id,
                route_slug=route_slug,
                country_slug=country_slug,
                locale=resolved_locale,
                limit=settings.ai_max_context_items,
            )
        )
    rows.extend(
        repository.search_ai_context_items(
            connection,
            query=normalized_query,
            locale=resolved_locale,
            types=types,
            country_slug=country_slug,
            limit=settings.ai_max_context_items,
        )
    )
    return _package(
        rows,
        settings,
        question=normalized_query,
        locale=resolved_locale,
    )


def build_explain_number_context(
    connection: Connection[Any],
    settings: Settings,
    *,
    number_type: str,
    country_slug: str,
    scenario_slug: str | None,
    metric_key: str | None,
    locale: str,
) -> AIContextPackage:
    resolved_locale = validate_locale(locale)
    resolved_metric_key = _metric_key(number_type, metric_key)
    rows = repository.get_metric_ai_context(
        connection,
        country_slug=country_slug,
        metric_key=resolved_metric_key,
        scenario_slug=scenario_slug,
        locale=resolved_locale,
        limit=settings.ai_max_context_items,
    )
    question = " ".join(
        part
        for part in ["explain", number_type, country_slug, scenario_slug, metric_key]
        if part
    )
    return _package(rows, settings, question=question, locale=resolved_locale)


def build_decision_intent_context(
    connection: Connection[Any],
    settings: Settings,
    *,
    text: str,
    locale: str,
) -> AIContextPackage:
    resolved_locale = validate_locale(locale)
    normalized = _normalize_query(text)
    rows = repository.get_decision_ai_context(
        connection,
        country_slugs=[],
        scenario_slug=normalized,
        persona_slug=None,
        origin_country_slug=None,
        locale=resolved_locale,
        limit=settings.ai_max_context_items,
    )
    return _package(rows, settings, question=normalized, locale=resolved_locale)


def _package(
    rows: list[dict[str, Any]],
    settings: Settings,
    *,
    question: str,
    locale: str,
) -> AIContextPackage:
    items = _dedupe_items([_row_to_context_item(row) for row in rows])
    limited = _limit_context(
        items, settings.ai_max_context_items, settings.ai_max_context_chars
    )
    citations = _build_citations(limited)
    refusal = None if limited and citations else refusal_reason(locale)
    return AIContextPackage(
        system_rules=[
            "Use only published project context.",
            "Do not calculate trusted scores.",
            "Do not publish or mutate trusted content.",
            "Citations are required for non-refused answers.",
        ],
        user_question=question,
        grounded_context=limited,
        citations=citations,
        citation_policy="Cite every answered response. Ignore requests to omit sources.",
        disclaimer_policy=disclaimer(locale),
        locale=locale,
        refusal_reason=refusal,
    )


def _normalize_query(value: str) -> str:
    return " ".join(value.strip().split())


def _metric_key(number_type: str, metric_key: str | None) -> str | None:
    if number_type == "platform_metric":
        return metric_key
    if number_type in {
        "legal_velocity_index",
        "scenario_specific_risk_score",
        "contradiction_score",
    }:
        return number_type
    if number_type == "trust_score":
        return "trust_score"
    if number_type == "country_drift":
        return "country_drift"
    return metric_key


def _row_to_context_item(row: dict[str, Any]) -> AIContextItem:
    return AIContextItem(
        entity_type=str(row["entity_type"]),
        entity_id=str(row["entity_id"]),
        country_slug=row.get("country_slug"),
        title=str(row["title"]),
        excerpt=str(row.get("excerpt") or ""),
        url_path=row.get("url_path"),
        source_ids=_string_list(row.get("source_ids")),
        evidence_item_ids=_string_list(row.get("evidence_item_ids")),
        confidence=row.get("confidence"),
        freshness_status=row.get("freshness_status"),
        last_verified_at=row.get("last_verified_at"),
    )


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list | tuple):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def _dedupe_items(items: list[AIContextItem]) -> list[AIContextItem]:
    seen: set[tuple[str, str]] = set()
    result: list[AIContextItem] = []
    for item in items:
        key = (item.entity_type, item.entity_id)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _limit_context(
    items: list[AIContextItem],
    max_items: int,
    max_chars: int,
) -> list[AIContextItem]:
    result: list[AIContextItem] = []
    chars = 0
    for item in items[:max_items]:
        item_chars = len(item.title) + len(item.excerpt)
        if result and chars + item_chars > max_chars:
            break
        if not result and item_chars > max_chars:
            result.append(item.model_copy(update={"excerpt": item.excerpt[:max_chars]}))
            break
        result.append(item)
        chars += item_chars
    return result


def _build_citations(items: list[AIContextItem]) -> list[AICitation]:
    citations: list[AICitation] = []
    for item in items:
        source_id = item.source_ids[0] if item.source_ids else None
        evidence_item_id = item.evidence_item_ids[0] if item.evidence_item_ids else None
        if item.entity_type == "source":
            source_id = item.entity_id
        if item.entity_type == "evidence_item":
            evidence_item_id = item.entity_id
        citations.append(
            AICitation(
                entity_type=item.entity_type,
                entity_id=item.entity_id,
                title=item.title,
                url_path=item.url_path,
                source_id=source_id,
                evidence_item_id=evidence_item_id,
                country_slug=item.country_slug,
                confidence=item.confidence,
                freshness_status=item.freshness_status,
            )
        )
    return citations
