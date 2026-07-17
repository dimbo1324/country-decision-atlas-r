from __future__ import annotations

from pydantic import BaseModel, ConfigDict


FICTIONAL_NOTICE = "SYNTHETIC TEST DATA - NOT REAL"


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class WorldMetadata(_FrozenModel):
    dataset_id: str
    schema_version: str
    generator_version: str
    seed: int
    profile: str
    supported_locales: tuple[str, ...]
    source_config_checksum: str
    generated_on: str
    fictional_notice: str = FICTIONAL_NOTICE


class MetricSnapshot(_FrozenModel):
    as_of: str
    metrics: dict[str, int]


class SyntheticEvent(_FrozenModel):
    event_id: str
    country_id: str
    as_of: str
    metric: str
    direction: str
    summary: str


class SyntheticSource(_FrozenModel):
    source_id: str
    country_id: str
    event_id: str
    title: str
    url: str
    confidence: int


class SyntheticCountry(_FrozenModel):
    country_id: str
    code: str
    slug: str
    name: str
    archetype: str
    metric_history: tuple[MetricSnapshot, ...]
    strengths: tuple[str, ...]
    risks: tuple[str, ...]
    uncertainties: tuple[str, ...]
    events: tuple[SyntheticEvent, ...]
    sources: tuple[SyntheticSource, ...]

    @property
    def current_metrics(self) -> dict[str, int]:
        return self.metric_history[-1].metrics


class SyntheticUser(_FrozenModel):
    user_id: str
    display_name: str
    email: str
    role: str
    locale: str


class SyntheticAuthor(_FrozenModel):
    author_id: str
    user_id: str
    display_name: str
    reputation: int
    specialization: str
    bio: str


class SyntheticArticle(_FrozenModel):
    article_id: str
    author_id: str
    country_id: str
    title: str
    summary: str
    source_ids: tuple[str, ...]
    published_as_of: str


class SyntheticComment(_FrozenModel):
    comment_id: str
    article_id: str
    user_id: str
    body: str
    created_as_of: str
    moderation_status: str


class SyntheticLegalSignal(_FrozenModel):
    signal_id: str
    country_id: str
    event_id: str
    affected_country_ids: tuple[str, ...]
    effective_as_of: str
    impact: str
    confidence: int
    source_id: str


class ResolvedBlock(_FrozenModel):
    block_id: str
    text: str


class SyntheticDocumentRecipe(_FrozenModel):
    recipe_id: str
    document_type: str
    country_id: str
    locale: str = "en-US"
    blocks: tuple[ResolvedBlock, ...]


class ScenarioStep(_FrozenModel):
    action: str
    target: dict[str, str]


class ScenarioExpectedResult(_FrozenModel):
    description: str
    check: str


class SyntheticScenario(_FrozenModel):
    scenario_id: str
    title: str
    category: str
    profile: str
    initial_state: dict[str, str]
    steps: tuple[ScenarioStep, ...]
    expected_results: tuple[ScenarioExpectedResult, ...]
    related_artifacts: tuple[str, ...]
    risk_labels: tuple[str, ...]


class SyntheticWorld(_FrozenModel):
    metadata: WorldMetadata
    countries: tuple[SyntheticCountry, ...]
    users: tuple[SyntheticUser, ...] = ()
    authors: tuple[SyntheticAuthor, ...] = ()
    articles: tuple[SyntheticArticle, ...] = ()
    comments: tuple[SyntheticComment, ...] = ()
    legal_signals: tuple[SyntheticLegalSignal, ...] = ()
    document_recipes: tuple[SyntheticDocumentRecipe, ...] = ()
    scenarios: tuple[SyntheticScenario, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return self.model_dump(mode="json")
