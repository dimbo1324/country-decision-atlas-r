from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID


DataErrorReportType = Literal[
    "outdated",
    "wrong",
    "missing_source",
    "contradiction",
    "translation_issue",
    "other",
]
DataErrorReportStatus = Literal["pending", "review", "resolved", "rejected", "archived"]
DataErrorReportIdentityType = Literal["telegram", "anonymous_session", "system"]


class DataErrorReportCreate(BaseModel):
    entity_type: str = Field(min_length=1, max_length=100)
    entity_id: str | None = Field(default=None, max_length=100)
    country_slug: str | None = Field(default=None, max_length=100)
    route_id: str | None = Field(default=None, max_length=100)
    report_type: DataErrorReportType
    message: str = Field(min_length=1, max_length=2000)
    created_by_identity_type: DataErrorReportIdentityType
    created_by_identity_id: str = Field(min_length=1, max_length=200)


class DataErrorReport(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID | None = None
    country_slug: str | None = None
    route_id: UUID | None = None
    report_type: DataErrorReportType
    message: str
    status: DataErrorReportStatus
    created_by_identity_type: DataErrorReportIdentityType
    created_by_identity_id: str
    created_at: datetime
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None
    resolution_note: str | None = None


class DataErrorReportListResponse(BaseModel):
    items: list[DataErrorReport]
    total: int


class DataErrorReportStatusUpdateRequest(BaseModel):
    status: DataErrorReportStatus
    reviewed_by: str | None = Field(default=None, max_length=200)
    resolution_note: str | None = Field(default=None, max_length=2000)
