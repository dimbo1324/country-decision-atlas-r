from dataclasses import dataclass
from decimal import Decimal
from typing import Any


GLOBAL_SCENARIO_SLUG = "__global__"
METHODOLOGY_VERSION = "v1.0"


@dataclass(frozen=True)
class PlatformMetricComputation:
    metric_key: str
    scenario_slug: str
    value: Decimal | None
    label: str
    confidence: str
    freshness_status: str
    window_days: int
    methodology_version: str
    input_summary: dict[str, Any]
    source_count: int
    evidence_count: int
    signal_count: int
    event_count: int
