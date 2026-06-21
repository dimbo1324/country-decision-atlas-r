from app.schemas.common import LocaleResolution, Pagination, SortMeta
from app.schemas.localization import LocalizationMeta
from datetime import date, datetime
from pydantic import BaseModel
from uuid import UUID


class Source(BaseModel):
    id: UUID
    title: str
    url: str
    source_type: str
    publisher: str | None = None
    country_id: UUID | None = None
    locale_id: UUID | None = None
    reliability_level: str
    language: str | None = None
    confidence: str | None = None
    status: str | None = None
    published_at: date | None = None
    accessed_at: date | None = None
    last_checked_at: date | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    localization: LocalizationMeta | None = None


class SourceListResponse(BaseModel):
    items: list[Source]
    pagination: Pagination
    sort: SortMeta | None = None
    locale: LocaleResolution


class SourceResponse(BaseModel):
    item: Source
    locale: LocaleResolution


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
    legal_signal_id: UUID | None = None
    claim: str | None = None
    excerpt: str | None = None
    retrieved_at: date | None = None
    confidence: str | None = None
    status: str | None = None
    published_at: date | None = None
    created_at: datetime
    updated_at: datetime
    localization: LocalizationMeta | None = None


class EvidenceItemListResponse(BaseModel):
    items: list[EvidenceItem]
    pagination: Pagination
    sort: SortMeta | None = None
    locale: LocaleResolution | None = None
