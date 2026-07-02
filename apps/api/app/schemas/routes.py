from app.schemas.common import (
    LegalStatus,
    LocaleResolution,
    Pagination,
    PublicationStatus,
)
from app.schemas.route_checklists import RouteChecklistItem
from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel
from uuid import UUID


class RouteType(StrEnum):
    temporary_residence = "temporary_residence"
    permanent_residence = "permanent_residence"
    citizenship = "citizenship"
    digital_nomad = "digital_nomad"
    work = "work"
    business = "business"
    study = "study"
    investment = "investment"


class EligibilityFlag(StrEnum):
    yes = "yes"
    no = "no"
    unknown = "unknown"


class RouteEligibility(BaseModel):
    allows_work: EligibilityFlag
    allows_family: EligibilityFlag
    leads_to_pr: EligibilityFlag
    leads_to_citizenship: EligibilityFlag
    requires_income_proof: EligibilityFlag
    requires_local_address: EligibilityFlag
    requires_criminal_record_check: EligibilityFlag


class RouteDocument(BaseModel):
    id: UUID
    name: str
    is_mandatory: bool
    note: str | None = None
    display_order: int


class RouteSourceRef(BaseModel):
    id: UUID
    title: str
    url: str
    source_type: str | None = None
    publisher: str | None = None
    confidence: str | None = None
    country_slug: str | None = None


class RouteEvidenceRef(BaseModel):
    id: UUID
    claim: str | None = None
    excerpt: str | None = None
    source_id: UUID | None = None
    source_title: str | None = None
    source_url: str | None = None
    confidence: str | None = None
    country_slug: str | None = None


class RouteListItem(BaseModel):
    id: UUID
    country_slug: str
    route_type: RouteType
    slug: str
    title: str
    summary: str | None = None
    eligibility_summary: str | None = None
    eligibility: RouteEligibility
    legal_status: LegalStatus
    status: PublicationStatus
    updated_at: datetime


class RouteListResponse(BaseModel):
    items: list[RouteListItem]
    pagination: Pagination
    locale: LocaleResolution


class RouteDetailResponse(BaseModel):
    id: UUID
    country_slug: str
    route_type: RouteType
    slug: str
    title: str
    summary: str | None = None
    eligibility_summary: str | None = None
    income_requirement_note: str | None = None
    fees_note: str | None = None
    processing_time_note: str | None = None
    stay_period_note: str | None = None
    renewal_note: str | None = None
    tax_warning: str | None = None
    legal_warning: str | None = None
    eligibility: RouteEligibility
    legal_status: LegalStatus
    status: PublicationStatus
    updated_at: datetime
    documents: list[RouteDocument]
    sources: list[RouteSourceRef]
    evidence: list[RouteEvidenceRef]
    checklist: list[RouteChecklistItem]
    locale: LocaleResolution
