from datetime import datetime
from pydantic import BaseModel
from typing import Any


class ModerationActionEntry(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    action: str
    changed_by: str
    changed_at: datetime
    changes: dict[str, Any]


class ModeratorAnomaly(BaseModel):
    changed_by: str
    total_actions: int
    reject_like_actions: int
    reject_rate: float


class ModerationActionListResponse(BaseModel):
    items: list[ModerationActionEntry]
    total: int
    anomalies: list[ModeratorAnomaly]
