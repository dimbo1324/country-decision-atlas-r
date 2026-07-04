from app.schemas.decision_engine import DecisionRunRequest, DecisionRunResponse
from app.schemas.decision_personalization import DecisionWeightItem
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


PassportStatus = Literal["active", "expired", "revoked"]


class DecisionPassportSourceRef(BaseModel):
    id: str
    title: str
    url: str


class DecisionPassportRouteRef(BaseModel):
    id: str
    title: str
    country_slug: str | None = None


class DecisionPassportMethodologySnapshot(BaseModel):
    decision_engine_version: str
    methodology_version: str
    scenario_slug: str
    persona_slug: str | None = None
    origin_country_slug: str | None = None
    weight_profile_id: str | None = None
    weight_profile_name: str | None = None
    custom_weights_applied: bool
    weight_mode: str
    applied_weights: list[DecisionWeightItem]
    ranking_policy: str
    disclaimer: str
    generated_at: datetime


class DecisionPassportCreateRequest(BaseModel):
    decision_request: DecisionRunRequest
    locale: Literal["en", "ru"] = "ru"
    expires_in_days: int | None = Field(default=None, ge=1, le=365)


class DecisionPassportCreateResponse(BaseModel):
    passport_id: str
    token: str
    path: str
    expires_at: datetime | None = None
    generated_at: datetime


class DecisionPassportResponse(BaseModel):
    id: str
    locale: Literal["en", "ru"]
    scenario_slug: str
    persona_slug: str | None = None
    origin_country_slug: str | None = None
    candidate_country_slugs: list[str]
    selected_country_slug: str | None = None
    decision_result: DecisionRunResponse
    methodology_version: str
    methodology_snapshot: DecisionPassportMethodologySnapshot
    source_ids: list[str] = Field(default_factory=list)
    route_ids: list[str] = Field(default_factory=list)
    source_refs: list[DecisionPassportSourceRef] = Field(default_factory=list)
    route_refs: list[DecisionPassportRouteRef] = Field(default_factory=list)
    disclaimer: str
    generated_at: datetime
    expires_at: datetime | None = None
    status: PassportStatus
