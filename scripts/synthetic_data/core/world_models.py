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


class SyntheticWorld(_FrozenModel):
    metadata: WorldMetadata
    countries: tuple[SyntheticCountry, ...]

    def to_dict(self) -> dict[str, object]:
        return self.model_dump(mode="json")
