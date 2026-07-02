from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


WhatChangedEventType = Literal[
    "legal_signal_published",
    "route_published",
    "route_updated",
    "drift_changed",
    "source_added",
    "evidence_added",
    "trust_updated",
    "platform_metric_updated",
]

WhatChangedImportance = Literal["low", "medium", "high", "critical"]


class WhatChangedItem(BaseModel):
    id: str
    event_type: WhatChangedEventType
    entity_type: str
    entity_id: str
    country_slug: str
    title: str
    summary: str
    path: str
    occurred_at: datetime
    importance: WhatChangedImportance
    source: str


class WhatChangedSummary(BaseModel):
    total: int = 0
    legal_signals: int = 0
    routes: int = 0
    drift: int = 0
    sources: int = 0


class WhatChangedResponse(BaseModel):
    country_slug: str
    since: datetime
    generated_at: datetime
    summary: WhatChangedSummary
    items: list[WhatChangedItem] = Field(default_factory=list)
