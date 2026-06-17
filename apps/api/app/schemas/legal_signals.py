from datetime import date, datetime
from typing import Literal
from uuid import UUID

from app.schemas.common import LocaleResolution, Pagination
from pydantic import BaseModel

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
SignalStatus = Literal["draft", "proposed", "adopted", "rejected", "active", "expired", "unknown"]
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
    locale: LocaleResolution


class LegalSignalCreate(BaseModel):
    country_id: UUID
    title: str
    summary: str
    signal_type: SignalType
    sentiment: Sentiment = "unknown"
    severity: Severity = "low"
    status: SignalStatus = "draft"
    confidence_level: ConfidenceLevel = "low"
    effective_date: date | None = None
    published_at: date | None = None


class LegalSignalResponse(BaseModel):
    item: LegalSignal
