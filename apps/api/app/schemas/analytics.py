from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Annotated, Any
from uuid import UUID


class AnalyticsSource(StrEnum):
    web = "web"
    api = "api"
    worker = "worker"
    notifier = "notifier"
    unknown = "unknown"


class AnalyticsEventCreate(BaseModel):
    event_type: Annotated[
        str,
        Field(min_length=2, max_length=64, pattern=r"^[a-z][a-z0-9_]{1,63}$"),
    ]
    session_id: Annotated[str, Field(min_length=8, max_length=256)]
    source: AnalyticsSource = AnalyticsSource.web
    path: Annotated[str, Field(max_length=512)] | None = None
    locale: Annotated[str, Field(max_length=16)] | None = None
    country_slug: Annotated[str, Field(max_length=80)] | None = None
    scenario_slug: Annotated[str, Field(max_length=80)] | None = None
    persona_slug: Annotated[str, Field(max_length=80)] | None = None
    route_id: UUID | None = None
    entity_type: Annotated[str, Field(max_length=80)] | None = None
    entity_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalyticsEventCreateResponse(BaseModel):
    accepted: bool
    stored: bool
    event_id: UUID | None = None
    reason: str | None = None
