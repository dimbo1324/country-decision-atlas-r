from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field


class FeatureFlagStatus(StrEnum):
    enabled = "enabled"
    disabled = "disabled"
    internal = "internal"
    deprecated = "deprecated"


class FeatureAccessTier(StrEnum):
    public = "public"
    beta = "beta"
    internal = "internal"
    admin = "admin"


class FeatureFlag(BaseModel):
    key: str
    name: str
    description: str | None = None
    status: FeatureFlagStatus
    access_tier: FeatureAccessTier
    default_enabled: bool
    is_enabled_for_context: bool
    decision_reason: str


class FeatureAccessRule(BaseModel):
    feature_key: str
    access_tier: FeatureAccessTier
    is_enabled: bool
    created_at: datetime | None = None


class FeatureAccessContext(BaseModel):
    access_tier: FeatureAccessTier = FeatureAccessTier.public
    environment: str = Field(default="local", pattern="^(local|production)$")
    is_admin: bool = False


class FeatureAccessDecision(BaseModel):
    feature_key: str
    is_enabled: bool
    reason: str
    access_tier: FeatureAccessTier
    status: FeatureFlagStatus | None = None


class FeatureFlagListResponse(BaseModel):
    items: list[FeatureFlag]
    context: FeatureAccessContext


class FeatureFlagDetailResponse(BaseModel):
    item: FeatureFlag
    decision: FeatureAccessDecision
    context: FeatureAccessContext
    access_rules: list[FeatureAccessRule] = Field(default_factory=list)
