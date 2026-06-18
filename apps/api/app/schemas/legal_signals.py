from app.schemas.common import LocaleResolution, Pagination, PublicationStatus, SortMeta
from datetime import date, datetime
from pydantic import BaseModel
from typing import Literal
from uuid import UUID


SignalType = Literal[
    "law",
    "bill",
    "policy",
    "court_decision",
    "administrative_change",
    "political_signal",
    "other",
]
Sentiment = Literal["positive", "neutral", "negative", "mixed", "unknown"]
Severity = Literal["low", "medium", "high", "critical"]
SignalStatus = PublicationStatus
ConfidenceLevel = Literal["low", "medium", "high"]


class LegalSignal(BaseModel):
    id: UUID
    country_id: UUID
    title: str
    summary: str
    signal_type: SignalType
    sentiment: Sentiment
    severity: Severity
    status: SignalStatus
    confidence_level: ConfidenceLevel
    effective_date: date | None = None
    published_at: date | None = None
    created_at: datetime
    updated_at: datetime


class LegalSignalListResponse(BaseModel):
    items: list[LegalSignal]
    pagination: Pagination
    sort: SortMeta | None = None
    locale: LocaleResolution


class LegalSignalCreate(BaseModel):
    country_id: UUID
    title: str
    summary: str
    signal_type: SignalType
    sentiment: Sentiment = "unknown"
    severity: Severity = "low"
    status: SignalStatus = PublicationStatus.draft
    confidence_level: ConfidenceLevel = "low"
    effective_date: date | None = None
    published_at: date | None = None


class LegalSignalResponse(BaseModel):
    item: LegalSignal
