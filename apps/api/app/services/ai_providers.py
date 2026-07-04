from app.core.config import Settings, get_settings
from app.schemas.ai import (
    AIAskResponse,
    AICitation,
    AIContextItem,
    AIDecisionIntentResponse,
    AIDecisionIntentResult,
    AIExplainNumberResponse,
    AIProviderMeta,
    AIRefusal,
    AIWarning,
)
from app.services.ai_context import disclaimer
from typing import Protocol


class AIProvider(Protocol):
    provider: str
    model: str
    mode: str
    grounded: bool

    def answer_question(
        self,
        *,
        question: str,
        locale: str,
        context_items: list[AIContextItem],
        citations: list[AICitation],
        refusal_reason: str | None,
    ) -> AIAskResponse: ...

    def explain_number(
        self,
        *,
        number_type: str,
        value: float | None,
        locale: str,
        context_items: list[AIContextItem],
        citations: list[AICitation],
        refusal_reason: str | None,
    ) -> AIExplainNumberResponse: ...

    def parse_decision_intent(
        self,
        *,
        text: str,
        locale: str,
        context_items: list[AIContextItem],
        citations: list[AICitation],
        refusal_reason: str | None,
    ) -> AIDecisionIntentResponse: ...


class FakeAIProvider:
    def __init__(
        self, model: str = "fake-grounded-v1", mode: str = "fake"
    ) -> None:
        self.provider = "fake"
        self.model = model
        self.mode = mode
        self.grounded = True

    def answer_question(
        self,
        *,
        question: str,
        locale: str,
        context_items: list[AIContextItem],
        citations: list[AICitation],
        refusal_reason: str | None,
    ) -> AIAskResponse:
        if refusal_reason is not None:
            return AIAskResponse(
                answer=refusal_reason,
                refused=True,
                citations=[],
                context_items_count=0,
                warnings=[_warning(locale, "insufficient_context")],
                disclaimer=disclaimer(locale),
                provider=self.provider,
                model=self.model,
                mode=self.mode,
                grounded=self.grounded,
                provider_meta=_provider_meta(self),
                refusal=AIRefusal(reason=refusal_reason),
            )
        answer = _answer_text(len(context_items), question, context_items)
        return AIAskResponse(
            answer=answer,
            refused=False,
            citations=citations,
            context_items_count=len(context_items),
            warnings=[],
            disclaimer=disclaimer(locale),
            provider=self.provider,
            model=self.model,
            mode=self.mode,
            grounded=self.grounded,
            provider_meta=_provider_meta(self),
        )

    def explain_number(
        self,
        *,
        number_type: str,
        value: float | None,
        locale: str,
        context_items: list[AIContextItem],
        citations: list[AICitation],
        refusal_reason: str | None,
    ) -> AIExplainNumberResponse:
        if refusal_reason is not None:
            return AIExplainNumberResponse(
                explanation=refusal_reason,
                what_it_means=refusal_reason,
                what_it_does_not_mean=_does_not_mean(locale),
                citations=[],
                confidence=None,
                freshness_status=None,
                disclaimer=disclaimer(locale),
                provider=self.provider,
                model=self.model,
                mode=self.mode,
                grounded=self.grounded,
                provider_meta=_provider_meta(self),
                refused=True,
                warnings=[_warning(locale, "insufficient_context")],
                context_items_count=0,
                refusal=AIRefusal(reason=refusal_reason),
            )
        first = context_items[0]
        value_text = "n/a" if value is None else f"{value:g}"
        if locale == "ru":
            explanation = (
                f"[FAKE AI] Число {number_type}={value_text} объясняется только "
                f"по {len(context_items)} опубликованным контекстным элементам."
            )
            what_it_means = (
                f"Доступный контекст указывает на: {first.excerpt[:220]}"
            )
        else:
            explanation = (
                f"[FAKE AI] The {number_type}={value_text} number is explained "
                f"only from {len(context_items)} published context items."
            )
            what_it_means = (
                f"The available context indicates: {first.excerpt[:220]}"
            )
        return AIExplainNumberResponse(
            explanation=explanation,
            what_it_means=what_it_means,
            what_it_does_not_mean=_does_not_mean(locale),
            citations=citations,
            confidence=first.confidence,
            freshness_status=first.freshness_status,
            disclaimer=disclaimer(locale),
            provider=self.provider,
            model=self.model,
            mode=self.mode,
            grounded=self.grounded,
            provider_meta=_provider_meta(self),
            refused=False,
            warnings=[],
            context_items_count=len(context_items),
        )

    def parse_decision_intent(
        self,
        *,
        text: str,
        locale: str,
        context_items: list[AIContextItem],
        citations: list[AICitation],
        refusal_reason: str | None,
    ) -> AIDecisionIntentResponse:
        if refusal_reason is not None:
            result = AIDecisionIntentResult(
                clarifying_questions=[_clarifying_question(locale)],
                confidence="low",
            )
            return AIDecisionIntentResponse(
                result=result,
                clarifying_questions=result.clarifying_questions,
                confidence=result.confidence,
                citations=[],
                disclaimer=disclaimer(locale),
                provider=self.provider,
                model=self.model,
                mode=self.mode,
                grounded=self.grounded,
                provider_meta=_provider_meta(self),
                refused=True,
                warnings=[_warning(locale, "insufficient_context")],
                context_items_count=0,
                refusal=AIRefusal(reason=refusal_reason),
            )
        result = _intent_result(text, context_items, locale)
        return AIDecisionIntentResponse(
            result=result,
            scenario_slug=result.scenario_slug,
            persona_slug=result.persona_slug,
            origin_country_slug=result.origin_country_slug,
            candidate_country_slugs=result.candidate_country_slugs,
            route_filters=result.route_filters,
            weight_hints=result.weight_hints,
            clarifying_questions=result.clarifying_questions,
            confidence=result.confidence,
            citations=citations,
            disclaimer=disclaimer(locale),
            provider=self.provider,
            model=self.model,
            mode=self.mode,
            grounded=self.grounded,
            provider_meta=_provider_meta(self),
            refused=False,
            warnings=[],
            context_items_count=len(context_items),
        )


def get_ai_provider(settings: Settings | None = None) -> AIProvider:
    resolved = settings or get_settings()
    return FakeAIProvider(model=resolved.ai_model, mode=resolved.ai_mode)


def _provider_meta(provider: FakeAIProvider) -> AIProviderMeta:
    return AIProviderMeta(
        provider=provider.provider,
        model=provider.model,
        mode=provider.mode,
        grounded=provider.grounded,
    )


def _answer_text(
    count: int,
    question: str,
    context_items: list[AIContextItem],
) -> str:
    first = context_items[0]
    return (
        f"[FAKE AI] Based on {count} published context items for "
        f"“{question[:120]}”, the most relevant fragment is: {first.excerpt[:260]}"
    )


def _warning(locale: str, code: str) -> AIWarning:
    message = (
        "Недостаточно опубликованных данных для надёжного ответа."
        if locale == "ru"
        else "There is not enough published data for a reliable answer."
    )
    return AIWarning(code=code, message=message)


def _does_not_mean(locale: str) -> str:
    if locale == "ru":
        return "Это не пересчёт показателя, не прогноз и не юридическая консультация."
    return "This is not a recalculation, forecast, or legal advice."


def _intent_result(
    text: str,
    context_items: list[AIContextItem],
    locale: str,
) -> AIDecisionIntentResult:
    lowered = text.casefold()
    scenario_slug = "relocation_residence"
    persona_slug = "relocator"
    if any(
        token in lowered for token in ["бизнес", "business", "self-employed"]
    ):
        scenario_slug = "business_self_employment"
        persona_slug = "investor"
    elif any(
        token in lowered for token in ["сем", "family", "children", "дет"]
    ):
        scenario_slug = "permanent_residence_citizenship"
        persona_slug = "family"
    elif any(token in lowered for token in ["бюджет", "budget", "low cost"]):
        scenario_slug = "low_budget_living"
        persona_slug = "relocator"
    elif any(token in lowered for token in ["безопас", "safety", "risk"]):
        scenario_slug = "safety_political_risk"
    country_slugs = _candidate_country_slugs(context_items)
    if not country_slugs:
        country_slugs = ["uruguay", "argentina"]
    weight_hints = {
        "safety_score": 25.0
        if "безопас" in lowered or "safety" in lowered
        else 15.0,
        "long_term_status_score": 25.0 if "граждан" in lowered else 15.0,
        "cost_of_living_score": 25.0
        if "бюджет" in lowered or "budget" in lowered
        else 15.0,
    }
    questions = [
        "Уточните бюджет, состав семьи и срок переезда."
        if locale == "ru"
        else "Clarify budget, family composition, and relocation timeline."
    ]
    return AIDecisionIntentResult(
        scenario_slug=scenario_slug,
        persona_slug=persona_slug,
        origin_country_slug="russia"
        if "росси" in lowered or "russia" in lowered
        else None,
        candidate_country_slugs=country_slugs[:3],
        route_filters={
            "requires_family": "сем" in lowered or "family" in lowered
        },
        weight_hints=weight_hints,
        clarifying_questions=questions,
        confidence="medium",
    )


def _candidate_country_slugs(context_items: list[AIContextItem]) -> list[str]:
    result: list[str] = []
    for item in context_items:
        if item.country_slug and item.country_slug not in result:
            result.append(item.country_slug)
    return result


def _clarifying_question(locale: str) -> str:
    if locale == "ru":
        return "Уточните страну, маршрут или сценарий, чтобы найти опубликованный контекст."
    return "Clarify country, route, or scenario to find published context."
