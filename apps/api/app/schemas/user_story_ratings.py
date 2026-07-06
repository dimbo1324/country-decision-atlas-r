from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID


UserStoryRatingStatus = Literal[
    "pending", "review", "published", "rejected", "archived"
]
UserStoryRatingIdentityType = Literal["telegram", "anonymous_session", "system"]


class UserStoryRatingCreate(BaseModel):
    user_story_id: str | None = Field(default=None, max_length=100)
    country_slug: str | None = Field(default=None, max_length=100)
    route_id: str | None = Field(default=None, max_length=100)
    official_expectation_score: int | None = Field(default=None, ge=0, le=100)
    real_experience_score: int | None = Field(default=None, ge=0, le=100)
    bureaucracy_score: int | None = Field(default=None, ge=0, le=100)
    cost_surprise_score: int | None = Field(default=None, ge=0, le=100)
    banking_difficulty_score: int | None = Field(default=None, ge=0, le=100)
    safety_feeling_score: int | None = Field(default=None, ge=0, le=100)
    comment: str | None = Field(default=None, max_length=2000)
    created_by_identity_type: UserStoryRatingIdentityType | None = None
    created_by_identity_id: str | None = Field(default=None, max_length=200)


class UserStoryRating(BaseModel):
    id: UUID
    user_story_id: UUID | None = None
    country_slug: str | None = None
    route_id: UUID | None = None
    official_expectation_score: int | None = None
    real_experience_score: int | None = None
    bureaucracy_score: int | None = None
    cost_surprise_score: int | None = None
    banking_difficulty_score: int | None = None
    safety_feeling_score: int | None = None
    comment: str | None = None
    status: UserStoryRatingStatus
    created_by_identity_type: UserStoryRatingIdentityType | None = None
    created_by_identity_id: str | None = None
    created_at: datetime
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None


class UserStoryRatingListResponse(BaseModel):
    items: list[UserStoryRating]
    total: int


class UserStoryRatingStatusUpdateRequest(BaseModel):
    status: UserStoryRatingStatus
