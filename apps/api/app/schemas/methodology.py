from datetime import datetime
from pydantic import BaseModel
from typing import Any


class MethodologySection(BaseModel):
    slug: str
    title: str
    summary: str
    body: str
    section_type: str
    display_order: int
    updated_at: datetime | None = None


class MethodologyListResponse(BaseModel):
    items: list[MethodologySection]


class MethodologyParameter(BaseModel):
    version: str
    param_key: str
    value_numeric: float | None = None
    value_json: Any | None = None
    description: str
    effective_from: datetime
    created_at: datetime


class MethodologyParametersResponse(BaseModel):
    version: str
    items: list[MethodologyParameter]
