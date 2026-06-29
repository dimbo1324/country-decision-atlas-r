from datetime import UTC, datetime
from pydantic import BaseModel, Field
from typing import Literal


DataJournalEntryType = Literal[
    "legal_signal_published",
    "route_published",
    "source_updated",
    "evidence_added",
    "country_profile_updated",
    "data_reviewed",
]


class DataJournalEntry(BaseModel):
    id: str
    entry_type: DataJournalEntryType
    country_slug: str
    entity_type: str
    entity_id: str
    title: str
    summary: str
    event_date: datetime
    source: str
    is_source_backed: bool
    last_verified_at: datetime | None = None


class CountryDataJournalResponse(BaseModel):
    country_slug: str
    locale: Literal["en", "ru"]
    items: list[DataJournalEntry] = Field(default_factory=list)
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=50)
    offset: int = Field(ge=0)
    last_verified_at: datetime | None = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
