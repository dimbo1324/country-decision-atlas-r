from datetime import UTC, datetime
from pydantic import BaseModel, Field


class DataQualityCheck(BaseModel):
    code: str
    status: str


class DataQualityIssue(BaseModel):
    code: str
    severity: str
    entity_type: str
    entity_id: str | None = None
    message: str
    details: dict[str, object] = Field(default_factory=dict)


class DataQualityReport(BaseModel):
    overall_status: str = "valid"
    valid: bool
    critical_issues_count: int = 0
    warnings_count: int = 0
    checks: list[DataQualityCheck] = Field(default_factory=list)
    issues: list[DataQualityIssue] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
