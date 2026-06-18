from pydantic import BaseModel, Field


class DataQualityIssue(BaseModel):
    code: str
    severity: str
    entity_type: str
    entity_id: str | None = None
    message: str
    details: dict[str, object] = Field(default_factory=dict)


class DataQualityReport(BaseModel):
    valid: bool
    issues: list[DataQualityIssue] = Field(default_factory=list)
