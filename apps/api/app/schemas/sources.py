from datetime import date, datetime
from uuid import UUID

from app.schemas.common import Pagination
from pydantic import BaseModel


class Source(BaseModel):
    id: UUID
    title: str
    url: str
    source_type: str
    publisher: str | None = None
    country_id: UUID | None = None
    locale_id: UUID | None = None
    reliability_level: str
    published_at: date | None = None
    accessed_at: date | None = None
    created_at: datetime
    updated_at: datetime


class SourceListResponse(BaseModel):
    items: list[Source]
    pagination: Pagination


class EvidenceItem(BaseModel):
    id: UUID
    source_id: UUID
    country_id: UUID | None = None
    title: str
    summary: str
    url: str | None = None
    quote: str | None = None
    evidence_type: str
    confidence_level: str
    published_at: date | None = None
    created_at: datetime
    updated_at: datetime


class EvidenceItemListResponse(BaseModel):
    items: list[EvidenceItem]
    pagination: Pagination
