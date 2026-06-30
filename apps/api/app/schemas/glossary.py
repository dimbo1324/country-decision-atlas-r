from datetime import datetime
from pydantic import BaseModel


class GlossaryTerm(BaseModel):
    slug: str
    term: str
    definition: str
    category: str
    related_terms: list[str] = []
    display_order: int
    updated_at: datetime | None = None


class GlossaryListResponse(BaseModel):
    items: list[GlossaryTerm]
