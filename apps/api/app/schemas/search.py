from pydantic import BaseModel, Field
from typing import Literal


SearchResultType = Literal[
    "country",
    "route",
    "route_checklist_item",
    "legal_signal",
    "source",
    "evidence_item",
    "country_pair_compatibility",
    "methodology",
    "glossary_term",
]


class SearchResultItem(BaseModel):
    id: str
    entity_type: SearchResultType
    entity_id: str
    country_slug: str | None = None
    title: str
    snippet: str
    path: str
    rank: float


class SearchResponse(BaseModel):
    query: str
    locale: Literal["en", "ru"]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=50)
    offset: int = Field(ge=0)
    items: list[SearchResultItem] = Field(default_factory=list)
