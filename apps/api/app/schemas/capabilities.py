from datetime import datetime
from pydantic import BaseModel


class CapabilityGrant(BaseModel):
    id: str
    user_id: str
    capability: str
    granted_by: str
    granted_at: datetime
    revoked_at: datetime | None = None
    note: str | None = None


class CapabilityGrantCreate(BaseModel):
    user_id: str
    capability: str
    note: str | None = None


class CapabilityGrantResponse(BaseModel):
    item: CapabilityGrant


class CapabilityGrantListResponse(BaseModel):
    items: list[CapabilityGrant]
    total: int
