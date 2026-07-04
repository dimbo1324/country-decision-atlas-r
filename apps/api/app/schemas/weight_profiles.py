from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Annotated


WeightProfileName = Annotated[str, Field(min_length=1, max_length=120)]
WeightProfileWeights = dict[str, Decimal]


class UserWeightProfile(BaseModel):
    id: str
    user_id: str
    name: str
    scenario_slug: str | None = None
    weights: dict[str, float]
    is_default: bool
    created_at: datetime
    updated_at: datetime


class UserWeightProfileCreate(BaseModel):
    name: WeightProfileName
    scenario_slug: str | None = None
    weights: WeightProfileWeights
    is_default: bool = False


class UserWeightProfilePatch(BaseModel):
    name: WeightProfileName | None = None
    scenario_slug: str | None = None
    weights: WeightProfileWeights | None = None
    is_default: bool | None = None


class UserWeightProfileResponse(BaseModel):
    item: UserWeightProfile


class UserWeightProfileListResponse(BaseModel):
    items: list[UserWeightProfile]
