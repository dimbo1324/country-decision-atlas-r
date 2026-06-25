from app.schemas.common import LegalStatus, PublicationStatus
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Any
from uuid import UUID


class AuditEvent(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    changed_by: str
    changed_at: datetime
    changes: dict[str, Any]


class SourceCreate(BaseModel):
    country_slug: str | None = None
    title: str
    url: str | None = None
    source_type: str | None = None
    publisher: str | None = None
    language: str | None = "en"
    confidence: str | None = "medium"
    published_at: date | None = None
    last_checked_at: date | None = None
    notes: str | None = None
    status: PublicationStatus = PublicationStatus.draft


class SourcePatch(BaseModel):
    title: str | None = None
    url: str | None = None
    source_type: str | None = None
    publisher: str | None = None
    language: str | None = None
    confidence: str | None = None
    published_at: date | None = None
    last_checked_at: date | None = None
    notes: str | None = None
    status: PublicationStatus | None = None


class EvidenceItemCreate(BaseModel):
    country_slug: str | None = None
    source_id: UUID | None = None
    legal_signal_id: UUID | None = None
    claim: str | None = None
    excerpt: str | None = None
    url: str | None = None
    confidence: str | None = "medium"
    status: PublicationStatus = PublicationStatus.draft


class EvidenceItemPatch(BaseModel):
    source_id: UUID | None = None
    legal_signal_id: UUID | None = None
    claim: str | None = None
    excerpt: str | None = None
    url: str | None = None
    confidence: str | None = None
    status: PublicationStatus | None = None


class LegalSignalCreate(BaseModel):
    country_slug: str
    source_id: UUID | None = None
    title_en: str | None = None
    title_ru: str | None = None
    summary_en: str | None = None
    summary_ru: str | None = None
    signal_type: str | None = None
    impact_direction: str | None = None
    impact_level: str | None = None
    legal_status: LegalStatus = LegalStatus.unknown
    affected_groups: list[str] = Field(default_factory=list)
    published_date: date | None = None
    effective_date: date | None = None
    confidence: str | None = "medium"
    status: PublicationStatus = PublicationStatus.draft


class LegalSignalPatch(BaseModel):
    source_id: UUID | None = None
    title_en: str | None = None
    title_ru: str | None = None
    summary_en: str | None = None
    summary_ru: str | None = None
    signal_type: str | None = None
    impact_direction: str | None = None
    impact_level: str | None = None
    legal_status: LegalStatus | None = None
    affected_groups: list[str] | None = None
    published_date: date | None = None
    effective_date: date | None = None
    confidence: str | None = None
    status: PublicationStatus | None = None


class CountryProfilePatch(BaseModel):
    locale: str = "en"
    executive_summary: str | None = None
    migration_overview: str | None = None
    tax_overview: str | None = None
    cost_of_living_overview: str | None = None
    business_overview: str | None = None
    safety_overview: str | None = None
    legal_signals_summary: str | None = None
    risk_summary: str | None = None
    source_summary: str | None = None
    status: PublicationStatus | None = None


class UserStoryAdminCreate(BaseModel):
    origin_country_slug: str | None = None
    destination_country_slug: str
    city: str | None = None
    year: int | None = Field(default=None, ge=1990, le=2100)
    scenario: str
    budget_initial_usd: Decimal | None = Field(default=None, ge=0)
    budget_monthly_usd: Decimal | None = Field(default=None, ge=0)
    legal_path: str | None = None
    documents_used: list[str] = Field(default_factory=list)
    problems: str | None = None
    positive_outcome: str | None = None
    negative_outcome: str | None = None
    advice: str | None = None
    satisfaction_score: Decimal | None = Field(default=None, ge=0, le=10)
    verification_status: str = "synthetic"
    status: PublicationStatus = PublicationStatus.draft
    is_synthetic: bool = True
    notes: str = "Synthetic example for MVP demonstration only."


class UserStoryPatch(BaseModel):
    origin_country_slug: str | None = None
    destination_country_slug: str | None = None
    city: str | None = None
    year: int | None = Field(default=None, ge=1990, le=2100)
    scenario: str | None = None
    budget_initial_usd: Decimal | None = Field(default=None, ge=0)
    budget_monthly_usd: Decimal | None = Field(default=None, ge=0)
    legal_path: str | None = None
    documents_used: list[str] | None = None
    problems: str | None = None
    positive_outcome: str | None = None
    negative_outcome: str | None = None
    advice: str | None = None
    satisfaction_score: Decimal | None = Field(default=None, ge=0, le=10)
    verification_status: str | None = None
    status: PublicationStatus | None = None
    is_synthetic: bool | None = None
    notes: str | None = None


class AdminSourceResponse(BaseModel):
    item: dict[str, Any]
    audit: AuditEvent | None = None


class AdminEvidenceItemResponse(BaseModel):
    item: dict[str, Any]
    audit: AuditEvent | None = None


class AdminLegalSignalResponse(BaseModel):
    item: dict[str, Any]
    audit: AuditEvent | None = None


class AdminCountryProfileResponse(BaseModel):
    item: dict[str, Any]
    audit: AuditEvent | None = None


class AdminUserStoryResponse(BaseModel):
    item: dict[str, Any]
    audit: AuditEvent | None = None
