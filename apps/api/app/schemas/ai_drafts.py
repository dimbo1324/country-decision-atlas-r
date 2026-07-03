from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Literal
from uuid import UUID


AIDraftType = Literal[
    "summary",
    "contradiction_candidate",
    "explanation",
    "source_digest",
    "evidence_digest",
]
AIDraftStatus = Literal["needs_review", "approved", "rejected", "archived"]
AIDraftConfidence = Literal["low", "medium", "high"]


class AIDraftGenerateSummaryRequest(BaseModel):
    country_slug: str | None = Field(default=None, max_length=100)
    route_id: str | None = Field(default=None, max_length=100)
    source_id: str | None = Field(default=None, max_length=100)
    evidence_item_id: str | None = Field(default=None, max_length=100)
    topic: str = Field(min_length=1, max_length=200)
    locale: Literal["ru", "en"] = "ru"


class AIDraftStatusUpdateRequest(BaseModel):
    status: AIDraftStatus
    reviewed_by: str | None = Field(default=None, max_length=200)


class AIDraft(BaseModel):
    id: UUID
    draft_type: AIDraftType
    status: AIDraftStatus
    country_slug: str | None = None
    route_id: UUID | None = None
    legal_signal_id: UUID | None = None
    source_id: UUID | None = None
    evidence_item_id: UUID | None = None
    title: str
    body: str
    summary: str | None = None
    detected_issue: str | None = None
    provider: str
    model_name: str
    model_version: str
    input_context: dict[str, Any] = Field(default_factory=dict)
    citations: list[dict[str, Any]] = Field(default_factory=list)
    confidence: AIDraftConfidence
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AIDraftListResponse(BaseModel):
    items: list[AIDraft]
    total: int
