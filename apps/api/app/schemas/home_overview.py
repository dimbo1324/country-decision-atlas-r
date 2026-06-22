from app.schemas.common import LocaleResolution
from datetime import UTC, date, datetime
from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID


class CountryOverviewCard(BaseModel):
    slug: str
    name: str
    iso2: str | None = None
    best_scenario_slug: str | None = None
    best_scenario_name: str | None = None
    best_score: float | None = None
    weakest_scenario_slug: str | None = None
    weakest_scenario_name: str | None = None
    weakest_score: float | None = None
    average_score: float | None = None
    confidence: str | None = None


class ScenarioWinner(BaseModel):
    scenario_slug: str
    scenario_name: str
    winner_country_slug: str | None = None
    winner_country_name: str | None = None
    winner_score: float | None = None
    runner_up_country_slug: str | None = None
    runner_up_country_name: str | None = None
    runner_up_score: float | None = None
    delta: float | None = None


class HomeMatrixCountry(BaseModel):
    slug: str
    name: str
    iso2: str | None = None


class HomeMatrixScenario(BaseModel):
    slug: str
    name: str
    display_order: int


class HomeMatrixCell(BaseModel):
    country_slug: str
    scenario_slug: str
    score: float | None = None
    confidence: str | None = None
    score_label: str | None = None


class HomeMatrixPreview(BaseModel):
    countries: list[HomeMatrixCountry] = Field(default_factory=list)
    scenarios: list[HomeMatrixScenario] = Field(default_factory=list)
    cells: list[HomeMatrixCell] = Field(default_factory=list)


class HomeLegalSourceRef(BaseModel):
    id: UUID
    title: str
    url: str


class LatestLegalEvent(BaseModel):
    country_slug: str
    country_name: str
    event_date: date
    title: str
    summary: str | None = None
    impact_direction: str
    impact_level: str
    source: HomeLegalSourceRef | None = None


class HomeKeyInsight(BaseModel):
    kind: str
    title: str
    summary: str
    severity: Literal["info", "positive", "warning", "risk"]
    target_url: str


class HomeOverviewLinks(BaseModel):
    countries_url: str = "/countries"
    decision_url: str = "/decision"
    compare_url: str = "/compare"
    legal_signals_url: str = "/legal-signals"


class HomeOverviewResponse(BaseModel):
    locale: LocaleResolution
    countries_summary: list[CountryOverviewCard] = Field(default_factory=list)
    scenario_winners: list[ScenarioWinner] = Field(default_factory=list)
    matrix_preview: HomeMatrixPreview
    latest_legal_events: list[LatestLegalEvent] = Field(default_factory=list)
    key_insights: list[HomeKeyInsight] = Field(default_factory=list)
    links: HomeOverviewLinks = Field(default_factory=HomeOverviewLinks)
    quality_warnings: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
