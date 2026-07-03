from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


WatchlistStatus = Literal["active", "archived"]
WatchlistCreatedSource = Literal["web", "telegram_linked", "imported", "admin"]


class WatchlistItem(BaseModel):
    id: str
    country_slug: str
    country_name: str
    status: WatchlistStatus
    notify_legal_signals: bool
    notify_drift_changes: bool
    notify_route_updates: bool
    notes: str | None = None
    created_source: WatchlistCreatedSource
    created_at: datetime
    updated_at: datetime


class WatchlistResponse(BaseModel):
    total: int = Field(ge=0)
    items: list[WatchlistItem] = Field(default_factory=list)


class WatchlistPreferencesUpdateRequest(BaseModel):
    notify_legal_signals: bool | None = None
    notify_drift_changes: bool | None = None
    notify_route_updates: bool | None = None
    notes: str | None = None


class WatchlistStatusResponse(BaseModel):
    country_slug: str
    saved: bool
