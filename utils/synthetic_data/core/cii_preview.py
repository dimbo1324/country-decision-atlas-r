from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from pydantic import BaseModel, ConfigDict
from utils.synthetic_data.core.world_models import (
    FICTIONAL_NOTICE,
    SyntheticCountry,
    SyntheticWorld,
)


FORMULA_VERSION = "syn-cii-preview-v1"
AGGREGATION_METHOD = "geometric"


@dataclass(frozen=True)
class SyntheticCiiMetricDefinition:
    slug: str
    polarity: str
    weight: float


# A wholly synthetic metric catalog derived from the 8 archetype dimensions
# -- distinct slugs from the real `cii_metric_definitions` catalog
# (rule_of_law/economic_freedom/political_stability/safety/corruption/
# digital_access) so a dashboard never confuses a fake score with a real
# one. `data_confidence` is deliberately excluded from the score itself
# and surfaced only as `confidence` (see `_confidence_label`): it measures
# data quality/trust, not country quality, and the invariant that derived
# trust-style metrics never mix into CII applies just as much to this
# preview as to the real product.
_METRIC_DEFINITIONS: tuple[SyntheticCiiMetricDefinition, ...] = (
    SyntheticCiiMetricDefinition("syn_economy", "positive", 0.20),
    SyntheticCiiMetricDefinition("syn_cost_of_living", "negative", 0.10),
    SyntheticCiiMetricDefinition("syn_safety", "positive", 0.20),
    SyntheticCiiMetricDefinition("syn_civil_freedoms", "positive", 0.15),
    SyntheticCiiMetricDefinition(
        "syn_institutional_stability", "positive", 0.15
    ),
    SyntheticCiiMetricDefinition(
        "syn_digital_infrastructure", "positive", 0.10
    ),
    SyntheticCiiMetricDefinition("syn_migration_openness", "positive", 0.10),
)
_ARCHETYPE_METRIC_BY_SLUG = {
    "syn_economy": "economy",
    "syn_cost_of_living": "cost_of_living",
    "syn_safety": "safety",
    "syn_civil_freedoms": "civil_freedoms",
    "syn_institutional_stability": "institutional_stability",
    "syn_digital_infrastructure": "digital_infrastructure",
    "syn_migration_openness": "migration_openness",
}


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class CiiPreviewMetricScore(_FrozenModel):
    metric_slug: str
    polarity: str
    weight: float
    raw_value: int
    normalized_value: float


class CiiCountryPreview(_FrozenModel):
    """A derived, fake CII score for one synthetic country -- built for
    previewing the CII card/comparison-matrix UI against believable
    numbers, never written to (or read from) the real `cii_metric_definitions`
    / `country_metric_values` / `country_cii_scores` tables. The real CII
    formula/weights are locked (invariant #2) and never touched by this
    generator; this only mimics the same geometric-mean shape with an
    entirely separate, `syn_`-prefixed metric catalog and made-up weights."""

    country_id: str
    country_slug: str
    country_name: str
    overall_score: float
    confidence: str
    metric_scores: tuple[CiiPreviewMetricScore, ...]
    formula_version: str
    aggregation_method: str
    seed: int
    generated_on: str
    fictional_notice: str = FICTIONAL_NOTICE


def _normalized_value(*, raw_value: int, polarity: str) -> float:
    return (
        float(raw_value) if polarity == "positive" else float(100 - raw_value)
    )


def _geometric_mean_score(
    metric_scores: tuple[CiiPreviewMetricScore, ...],
) -> float:
    weighted_log_sum = sum(
        score.weight * math.log(max(score.normalized_value, 1.0))
        for score in metric_scores
    )
    total_weight = sum(score.weight for score in metric_scores)
    return round(math.exp(weighted_log_sum / total_weight), 2)


def _confidence_label(data_confidence: int) -> str:
    if data_confidence >= 70:
        return "high"
    if data_confidence >= 40:
        return "medium"
    return "low"


def generate_cii_preview(
    world: SyntheticWorld,
    *,
    seed: int,
    generated_on: str | None = None,
) -> tuple[CiiCountryPreview, ...]:
    """Builds one fake CII preview per country in `world`, using only the
    already-generated archetype metrics -- no network, no database, no
    dependency on the real product's schema or methodology config."""
    resolved_generated_on = generated_on or date.today().isoformat()
    return tuple(
        _country_preview(
            country=country,
            seed=seed,
            generated_on=resolved_generated_on,
        )
        for country in world.countries
    )


def _country_preview(
    *, country: SyntheticCountry, seed: int, generated_on: str
) -> CiiCountryPreview:
    metrics = country.current_metrics
    metric_scores = tuple(
        CiiPreviewMetricScore(
            metric_slug=definition.slug,
            polarity=definition.polarity,
            weight=definition.weight,
            raw_value=metrics[_ARCHETYPE_METRIC_BY_SLUG[definition.slug]],
            normalized_value=_normalized_value(
                raw_value=metrics[_ARCHETYPE_METRIC_BY_SLUG[definition.slug]],
                polarity=definition.polarity,
            ),
        )
        for definition in _METRIC_DEFINITIONS
    )
    return CiiCountryPreview(
        country_id=country.country_id,
        country_slug=country.slug,
        country_name=country.name,
        overall_score=_geometric_mean_score(metric_scores),
        confidence=_confidence_label(metrics["data_confidence"]),
        metric_scores=metric_scores,
        formula_version=FORMULA_VERSION,
        aggregation_method=AGGREGATION_METHOD,
        seed=seed,
        generated_on=generated_on,
    )
