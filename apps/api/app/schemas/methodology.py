from datetime import datetime
from pydantic import BaseModel


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
