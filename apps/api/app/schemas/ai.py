from pydantic import BaseModel, Field
from typing import Any, Literal


AILocale = Literal["ru", "en"]
AIRequestType = Literal["ask", "explain_number", "decision_intent"]
AIMode = Literal["fake", "real", "off"]
AINumberType = Literal[
    "cii_score",
    "decision_score",
    "trust_score",
    "country_drift",
    "legal_velocity_index",
    "scenario_specific_risk_score",
    "contradiction_score",
    "platform_metric",
]
AIContextEntityType = Literal[
    "country",
    "route",
    "route_checklist_item",
    "legal_signal",
    "source",
    "evidence_item",
    "country_pair_compatibility",
    "methodology",
    "glossary_term",
    "platform_metric",
    "trust_score",
    "country_drift",
    "decision_score",
    "scenario",
    "persona",
]


class AICitation(BaseModel):
    entity_type: str
    entity_id: str
    title: str
    url_path: str | None = None
    source_id: str | None = None
    evidence_item_id: str | None = None
    country_slug: str | None = None
    confidence: str | None = None
    freshness_status: str | None = None


class AIProviderMeta(BaseModel):
    provider: str = "fake"
    model: str = "fake-grounded-v1"
    mode: AIMode = "fake"
    grounded: bool = True


class AIWarning(BaseModel):
    code: str
    message: str


class AIRefusal(BaseModel):
    reason: str


class AIContextItem(BaseModel):
    entity_type: str
    entity_id: str
    country_slug: str | None = None
    title: str
    excerpt: str
    url_path: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    evidence_item_ids: list[str] = Field(default_factory=list)
    confidence: str | None = None
    freshness_status: str | None = None
    last_verified_at: str | None = None


class AIAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    locale: AILocale = "ru"
    country_slug: str | None = Field(default=None, max_length=100)
    route_id: str | None = Field(default=None, max_length=100)
    route_slug: str | None = Field(default=None, max_length=100)
    scenario_slug: str | None = Field(default=None, max_length=100)
    persona_slug: str | None = Field(default=None, max_length=100)
    types: list[str] | None = None


class AIAskResponse(BaseModel):
    answer: str
    refused: bool
    citations: list[AICitation] = Field(default_factory=list)
    context_items_count: int = Field(ge=0)
    warnings: list[AIWarning] = Field(default_factory=list)
    disclaimer: str
    provider: str
    model: str
    mode: AIMode
    grounded: bool = True
    provider_meta: AIProviderMeta | None = None
    refusal: AIRefusal | None = None


class AIExplainNumberRequest(BaseModel):
    number_type: AINumberType
    country_slug: str = Field(min_length=1, max_length=100)
    scenario_slug: str | None = Field(default=None, max_length=100)
    persona_slug: str | None = Field(default=None, max_length=100)
    metric_key: str | None = Field(default=None, max_length=100)
    value: float | None = None
    locale: AILocale = "ru"


class AIExplainNumberResponse(BaseModel):
    explanation: str
    what_it_means: str
    what_it_does_not_mean: str
    citations: list[AICitation] = Field(default_factory=list)
    confidence: str | None = None
    freshness_status: str | None = None
    disclaimer: str
    provider: str
    model: str
    mode: AIMode
    grounded: bool = True
    provider_meta: AIProviderMeta | None = None
    refused: bool
    warnings: list[AIWarning] = Field(default_factory=list)
    context_items_count: int = Field(ge=0)
    refusal: AIRefusal | None = None


class AIDecisionIntentRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    locale: AILocale = "ru"


class AIDecisionIntentResult(BaseModel):
    scenario_slug: str | None = None
    persona_slug: str | None = None
    origin_country_slug: str | None = None
    candidate_country_slugs: list[str] = Field(default_factory=list)
    route_filters: dict[str, Any] = Field(default_factory=dict)
    weight_hints: dict[str, float] = Field(default_factory=dict)
    clarifying_questions: list[str] = Field(default_factory=list)
    confidence: str = "low"


class AIDecisionIntentResponse(BaseModel):
    result: AIDecisionIntentResult
    scenario_slug: str | None = None
    persona_slug: str | None = None
    origin_country_slug: str | None = None
    candidate_country_slugs: list[str] = Field(default_factory=list)
    route_filters: dict[str, Any] = Field(default_factory=dict)
    weight_hints: dict[str, float] = Field(default_factory=dict)
    clarifying_questions: list[str] = Field(default_factory=list)
    confidence: str = "low"
    citations: list[AICitation] = Field(default_factory=list)
    disclaimer: str
    provider: str
    model: str
    mode: AIMode
    grounded: bool = True
    provider_meta: AIProviderMeta | None = None
    refused: bool
    warnings: list[AIWarning] = Field(default_factory=list)
    context_items_count: int = Field(ge=0)
    refusal: AIRefusal | None = None
