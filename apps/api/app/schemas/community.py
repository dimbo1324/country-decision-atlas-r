from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID


CommunityIdentityType = Literal["telegram", "anonymous_session", "system"]
CommunityModerationStatus = Literal[
    "pending", "review", "published", "rejected", "archived"
]
CommunityVoteType = Literal["up", "down", "helpful", "outdated"]


class CommunityQuestionCreate(BaseModel):
    country_slug: str | None = Field(default=None, max_length=100)
    route_id: str | None = Field(default=None, max_length=100)
    legal_signal_id: str | None = Field(default=None, max_length=100)
    topic: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1, max_length=4000)
    created_by_identity_type: CommunityIdentityType
    created_by_identity_id: str = Field(min_length=1, max_length=200)


class CommunityQuestion(BaseModel):
    id: UUID
    country_slug: str | None = None
    route_id: UUID | None = None
    legal_signal_id: UUID | None = None
    topic: str
    title: str
    body: str
    status: CommunityModerationStatus
    created_by_identity_type: CommunityIdentityType
    created_by_identity_id: str
    created_at: datetime
    updated_at: datetime
    moderated_at: datetime | None = None
    moderated_by: str | None = None


class CommunityQuestionListResponse(BaseModel):
    items: list[CommunityQuestion]
    total: int


class CommunityAnswerCreate(BaseModel):
    body: str = Field(min_length=1, max_length=4000)
    source_ids: list[str] = Field(default_factory=list)
    evidence_item_ids: list[str] = Field(default_factory=list)
    created_by_identity_type: CommunityIdentityType
    created_by_identity_id: str = Field(min_length=1, max_length=200)


class VoteSummary(BaseModel):
    up_votes: int = 0
    down_votes: int = 0
    helpful_votes: int = 0
    outdated_votes: int = 0


class ConsensusSummary(BaseModel):
    answer_id: str
    score: float
    source_backed: bool
    controversial: bool
    votes: VoteSummary


class CommunityAnswer(BaseModel):
    id: UUID
    question_id: UUID
    body: str
    status: CommunityModerationStatus
    source_ids: list[str] = Field(default_factory=list)
    evidence_item_ids: list[str] = Field(default_factory=list)
    created_by_identity_type: CommunityIdentityType
    created_by_identity_id: str
    created_at: datetime
    updated_at: datetime
    moderated_at: datetime | None = None
    moderated_by: str | None = None
    source_backed: bool = False
    consensus: ConsensusSummary | None = None


class CommunityAnswerListResponse(BaseModel):
    items: list[CommunityAnswer]
    total: int


class CommunityVoteCreate(BaseModel):
    vote_type: CommunityVoteType
    identity_type: CommunityIdentityType
    identity_id: str = Field(min_length=1, max_length=200)


class CommunityStatusUpdateRequest(BaseModel):
    status: CommunityModerationStatus
