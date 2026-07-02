from app.core.config import Settings, get_settings
from app.core.database import get_connection
from app.core.errors import api_error
from app.repositories import ai_interactions, feature_flags as feature_repository
from app.schemas.ai import (
    AIAskRequest,
    AIAskResponse,
    AIDecisionIntentRequest,
    AIDecisionIntentResponse,
    AIExplainNumberRequest,
    AIExplainNumberResponse,
)
from app.schemas.feature_flags import FeatureAccessTier
from app.services import feature_flags as feature_service
from app.services.ai_context import (
    build_ask_context,
    build_decision_intent_context,
    build_explain_number_context,
)
from app.services.ai_providers import get_ai_provider
from fastapi import APIRouter, Depends
from hashlib import sha256
from psycopg import Connection
import re
from typing import Annotated, Any


router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/ask", response_model=AIAskResponse)
def ask_ai(
    payload: AIAskRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AIAskResponse:
    _ensure_ai_enabled(
        connection,
        settings,
        ["ai_augmentation", "ai_grounded_qa"],
        "ask",
        payload.locale,
        payload.country_slug,
        payload.scenario_slug,
        payload.persona_slug,
        payload.question,
    )
    package = build_ask_context(
        connection,
        settings,
        question=payload.question,
        locale=payload.locale,
        types=payload.types,
        country_slug=payload.country_slug,
        route_id=payload.route_id,
        route_slug=payload.route_slug,
    )
    provider = get_ai_provider(settings)
    response = provider.answer_question(
        question=package.user_question,
        locale=package.locale,
        context_items=package.grounded_context,
        citations=package.citations,
        refusal_reason=package.refusal_reason,
    )
    _log_interaction(
        connection,
        settings,
        request_type="ask",
        locale=payload.locale,
        country_slug=payload.country_slug,
        scenario_slug=payload.scenario_slug,
        persona_slug=payload.persona_slug,
        text=payload.question,
        provider=response.provider,
        provider_model=response.model,
        status="refused" if response.refused else "completed",
        refused=response.refused,
        grounded=response.grounded,
        context_items_count=response.context_items_count,
        citations_count=len(response.citations),
        error_code="insufficient_context" if response.refused else None,
    )
    return response


@router.post("/explain-number", response_model=AIExplainNumberResponse)
def explain_number(
    payload: AIExplainNumberRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AIExplainNumberResponse:
    _ensure_ai_enabled(
        connection,
        settings,
        ["ai_augmentation", "ai_explain_number"],
        "explain_number",
        payload.locale,
        payload.country_slug,
        payload.scenario_slug,
        payload.persona_slug,
        payload.number_type,
    )
    package = build_explain_number_context(
        connection,
        settings,
        number_type=payload.number_type,
        country_slug=payload.country_slug,
        scenario_slug=payload.scenario_slug,
        metric_key=payload.metric_key,
        locale=payload.locale,
    )
    provider = get_ai_provider(settings)
    response = provider.explain_number(
        number_type=payload.number_type,
        value=payload.value,
        locale=package.locale,
        context_items=package.grounded_context,
        citations=package.citations,
        refusal_reason=package.refusal_reason,
    )
    _log_interaction(
        connection,
        settings,
        request_type="explain_number",
        locale=payload.locale,
        country_slug=payload.country_slug,
        scenario_slug=payload.scenario_slug,
        persona_slug=payload.persona_slug,
        text=payload.number_type,
        provider=response.provider,
        provider_model=response.model,
        status="refused" if response.refused else "completed",
        refused=response.refused,
        grounded=response.grounded,
        context_items_count=response.context_items_count,
        citations_count=len(response.citations),
        error_code="insufficient_context" if response.refused else None,
    )
    return response


@router.post("/decision-intent", response_model=AIDecisionIntentResponse)
def decision_intent(
    payload: AIDecisionIntentRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AIDecisionIntentResponse:
    _ensure_ai_enabled(
        connection,
        settings,
        ["ai_augmentation", "ai_nl_decision"],
        "decision_intent",
        payload.locale,
        None,
        None,
        None,
        payload.text,
    )
    package = build_decision_intent_context(
        connection,
        settings,
        text=payload.text,
        locale=payload.locale,
    )
    provider = get_ai_provider(settings)
    response = provider.parse_decision_intent(
        text=payload.text,
        locale=package.locale,
        context_items=package.grounded_context,
        citations=package.citations,
        refusal_reason=package.refusal_reason,
    )
    _log_interaction(
        connection,
        settings,
        request_type="decision_intent",
        locale=payload.locale,
        country_slug=response.origin_country_slug,
        scenario_slug=response.scenario_slug,
        persona_slug=response.persona_slug,
        text=payload.text,
        provider=response.provider,
        provider_model=response.model,
        status="refused" if response.refused else "completed",
        refused=response.refused,
        grounded=response.grounded,
        context_items_count=response.context_items_count,
        citations_count=len(response.citations),
        error_code="insufficient_context" if response.refused else None,
    )
    return response


def _ensure_ai_enabled(
    connection: Connection[Any],
    settings: Settings,
    feature_keys: list[str],
    request_type: str,
    locale: str,
    country_slug: str | None,
    scenario_slug: str | None,
    persona_slug: str | None,
    text: str,
) -> None:
    if settings.ai_mode == "off":
        _log_interaction(
            connection,
            settings,
            request_type=request_type,
            locale=locale,
            country_slug=country_slug,
            scenario_slug=scenario_slug,
            persona_slug=persona_slug,
            text=text,
            provider=settings.ai_provider,
            provider_model=settings.ai_model,
            status="feature_disabled",
            refused=True,
            grounded=True,
            context_items_count=0,
            citations_count=0,
            error_code="ai_disabled",
        )
        raise api_error(403, "ai_disabled", "AI assistance is disabled.")
    context = feature_service.default_access_context(settings, FeatureAccessTier.public)
    for feature_key in feature_keys:
        feature = feature_repository.get_feature_flag(connection, feature_key)
        rules = feature_repository.list_feature_access_rules(connection, feature_key)
        decision = feature_service.can_access(context, feature, rules, feature_key)
        if not decision.is_enabled:
            _log_interaction(
                connection,
                settings,
                request_type=request_type,
                locale=locale,
                country_slug=country_slug,
                scenario_slug=scenario_slug,
                persona_slug=persona_slug,
                text=text,
                provider=settings.ai_provider,
                provider_model=settings.ai_model,
                status="feature_disabled",
                refused=True,
                grounded=True,
                context_items_count=0,
                citations_count=0,
                error_code=decision.reason,
            )
            raise api_error(
                403,
                "feature_disabled",
                "AI feature is disabled.",
                {"feature_key": feature_key, "reason": decision.reason},
            )


def _log_interaction(
    connection: Connection[Any],
    settings: Settings,
    *,
    request_type: str,
    locale: str,
    country_slug: str | None,
    scenario_slug: str | None,
    persona_slug: str | None,
    text: str,
    provider: str,
    provider_model: str,
    status: str,
    refused: bool,
    grounded: bool,
    context_items_count: int,
    citations_count: int,
    error_code: str | None,
) -> None:
    if not settings.ai_log_interactions:
        return
    ai_interactions.insert_ai_interaction_log(
        connection,
        request_type=request_type,
        locale=locale,
        country_slug=country_slug,
        scenario_slug=scenario_slug,
        persona_slug=persona_slug,
        provider=provider,
        provider_model=provider_model,
        ai_mode=settings.ai_mode,
        status=status,
        refused=refused,
        grounded=grounded,
        query_hash=_query_hash(text),
        sanitized_preview=_sanitized_preview(text),
        context_items_count=context_items_count,
        citations_count=citations_count,
        error_code=error_code,
        metadata={},
    )


def _query_hash(text: str) -> str:
    return sha256(" ".join(text.split()).encode("utf-8")).hexdigest()


def _sanitized_preview(text: str) -> str:
    preview = " ".join(text.split())[:160]
    preview = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[email]", preview)
    preview = re.sub(r"\+?\d[\d\s().-]{7,}\d", "[phone]", preview)
    return preview[:120]
