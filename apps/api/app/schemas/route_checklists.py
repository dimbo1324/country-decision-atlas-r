from pydantic import BaseModel
from uuid import UUID


class RouteChecklistItem(BaseModel):
    id: UUID
    step_order: int
    title: str
    description: str | None = None
    document_note: str | None = None
    cost_note: str | None = None
    timing_note: str | None = None
    official_requirement_note: str | None = None
    is_required: bool
    source_id: UUID | None = None
    evidence_item_id: UUID | None = None


class RouteChecklistResponse(BaseModel):
    items: list[RouteChecklistItem]
