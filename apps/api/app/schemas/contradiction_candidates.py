from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID


ContradictionSeverity = Literal["low", "medium", "high", "critical"]
ContradictionStatus = Literal["needs_review", "confirmed", "dismissed", "archived"]
ContradictionConfidence = Literal["low", "medium", "high"]


class ContradictionCandidateGenerateRequest(BaseModel):
    country_slug: str | None = Field(default=None, max_length=100)
    topic: str = Field(min_length=1, max_length=200)
    entity_type: str | None = Field(default=None, max_length=100)
    entity_id: str | None = Field(default=None, max_length=100)
    locale: Literal["ru", "en"] = "ru"


class ContradictionCandidateStatusUpdateRequest(BaseModel):
    status: ContradictionStatus
    reviewed_by: str | None = Field(default=None, max_length=200)


class ContradictionCandidate(BaseModel):
    id: UUID
    country_slug: str | None = None
    topic: str
    entity_type: str | None = None
    entity_id: UUID | None = None
    severity: ContradictionSeverity
    status: ContradictionStatus
    summary: str
    claim_a: str
    claim_b: str
    source_ids: list[str] = Field(default_factory=list)
    evidence_item_ids: list[str] = Field(default_factory=list)
    detected_by: str
    provider: str
    model_name: str
    model_version: str
    confidence: ContradictionConfidence
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None
    created_at: datetime
    updated_at: datetime


class ContradictionCandidateListResponse(BaseModel):
    items: list[ContradictionCandidate]
    total: int
