from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


TimelineWindow = str
BudgetRange = str
HouseholdType = str
MigrationStage = str
CompanionGoal = str
PostVisibility = str
PostStatus = str
ModerationStatus = str
ContactRequestStatus = str
ReportReason = str
ReportStatus = str
ThreadStatus = str


class MigrationBoardAuthorSafe(BaseModel):
    display_name: str = "Member"


class MigrationBoardCountryRef(BaseModel):
    id: str
    slug: str
    name: str


class MigrationBoardRouteRef(BaseModel):
    id: str
    slug: str
    title: str


class MigrationBoardScenarioRef(BaseModel):
    slug: str
    label: str


class MigrationBoardPersonaRef(BaseModel):
    slug: str
    label: str


class MigrationBoardPostBase(BaseModel):
    id: str
    title: str
    summary: str
    destination_country: MigrationBoardCountryRef
    origin_country: MigrationBoardCountryRef | None = None
    route: MigrationBoardRouteRef | None = None
    scenario: MigrationBoardScenarioRef | None = None
    persona: MigrationBoardPersonaRef | None = None
    target_city: str | None = None
    target_month: date | None = None
    timeline_window: TimelineWindow
    budget_range: BudgetRange
    household_type: HouseholdType
    migration_stage: MigrationStage
    companion_goal: CompanionGoal
    preferred_language: str
    visibility: PostVisibility
    contact_requests_enabled: bool
    tags: list[str] = Field(default_factory=list)


class MigrationBoardPostSummary(MigrationBoardPostBase):
    author: MigrationBoardAuthorSafe
    published_at: datetime | None = None


class MigrationBoardPostDetail(MigrationBoardPostSummary):
    created_at: datetime


class MigrationBoardPostListResponse(BaseModel):
    items: list[MigrationBoardPostSummary]
    total: int
    limit: int
    offset: int


class CreateMigrationBoardPostRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    destination_country_slug: str
    origin_country_slug: str | None = None
    route_id: str | None = None
    scenario_slug: str | None = None
    persona_slug: str | None = None
    title: str = Field(min_length=6, max_length=140)
    summary: str = Field(min_length=30, max_length=1200)
    target_city: str | None = Field(default=None, max_length=120)
    target_month: date | None = None
    timeline_window: TimelineWindow = "unknown"
    budget_range: BudgetRange = "undisclosed"
    household_type: HouseholdType = "undisclosed"
    migration_stage: MigrationStage = "researching"
    companion_goal: CompanionGoal = "info_exchange"
    preferred_language: str = Field(default="undisclosed", max_length=24)
    visibility: PostVisibility = "members_only"
    risk_acknowledged: bool = False
    legal_disclaimer_acknowledged: bool = False
    contact_requests_enabled: bool = True
    tags: list[str] = Field(default_factory=list, max_length=12)


class UpdateMigrationBoardPostRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    destination_country_slug: str | None = None
    origin_country_slug: str | None = None
    route_id: str | None = None
    scenario_slug: str | None = None
    persona_slug: str | None = None
    title: str | None = Field(default=None, min_length=6, max_length=140)
    summary: str | None = Field(default=None, min_length=30, max_length=1200)
    target_city: str | None = Field(default=None, max_length=120)
    target_month: date | None = None
    timeline_window: TimelineWindow | None = None
    budget_range: BudgetRange | None = None
    household_type: HouseholdType | None = None
    migration_stage: MigrationStage | None = None
    companion_goal: CompanionGoal | None = None
    preferred_language: str | None = Field(default=None, max_length=24)
    visibility: PostVisibility | None = None
    risk_acknowledged: bool | None = None
    legal_disclaimer_acknowledged: bool | None = None
    contact_requests_enabled: bool | None = None
    tags: list[str] | None = Field(default=None, max_length=12)


class MyMigrationBoardPost(MigrationBoardPostBase):
    status: PostStatus
    moderation_status: ModerationStatus
    risk_acknowledged: bool
    legal_disclaimer_acknowledged: bool
    created_at: datetime
    updated_at: datetime
    submitted_at: datetime | None = None
    published_at: datetime | None = None
    archived_at: datetime | None = None
    rejected_at: datetime | None = None
    moderation_reason: str | None = None


class MyMigrationBoardPostListResponse(BaseModel):
    items: list[MyMigrationBoardPost]
    total: int


class SubmitMigrationBoardPostResponse(BaseModel):
    post: MyMigrationBoardPost


class ArchiveMigrationBoardPostResponse(BaseModel):
    post: MyMigrationBoardPost


class CreateContactRequestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=20, max_length=800)


class ContactRequestResponse(BaseModel):
    id: str
    post_id: str
    post_title: str
    from_user_display_name: str
    to_user_display_name: str
    message: str
    status: ContactRequestStatus
    created_at: datetime
    responded_at: datetime | None = None
    cancelled_at: datetime | None = None
    response_note: str | None = None


class ContactRequestListResponse(BaseModel):
    items: list[ContactRequestResponse]
    total: int


class ContactRequestActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    response_note: str | None = Field(default=None, max_length=1000)


class ContactRequestActionResponse(BaseModel):
    request: ContactRequestResponse


class CreateMigrationBoardReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: ReportReason
    details: str | None = Field(default=None, max_length=1000)


class MigrationBoardReportResponse(BaseModel):
    id: str
    post_id: str | None = None
    contact_request_id: str | None = None
    reason: ReportReason
    details: str | None = None
    status: ReportStatus
    created_at: datetime
    reviewed_at: datetime | None = None
    resolution_note: str | None = None


class MigrationBoardReportListResponse(BaseModel):
    items: list[MigrationBoardReportResponse]
    total: int


class ReviewMigrationBoardReportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resolution_note: str | None = Field(default=None, max_length=1000)
    hide_post: bool = False


class ReviewMigrationBoardReportResponse(BaseModel):
    report: MigrationBoardReportResponse


class ModerateMigrationBoardPostRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    moderation_reason: str | None = Field(default=None, max_length=1000)


class AdminMigrationBoardPost(MyMigrationBoardPost):
    user_id: str
    author_display_name: str
    moderated_by: str | None = None
    moderated_at: datetime | None = None


class AdminMigrationBoardPostListResponse(BaseModel):
    items: list[AdminMigrationBoardPost]
    total: int


class ModerateMigrationBoardPostResponse(BaseModel):
    post: AdminMigrationBoardPost


class CompanionMatchPost(MigrationBoardPostSummary):
    match_reasons: list[str]


class CompanionMatchesResponse(BaseModel):
    items: list[CompanionMatchPost]
    total: int


class BlockUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str | None = Field(default=None, max_length=500)


class BlockedUserResponse(BaseModel):
    id: str
    blocked_user_id: str
    blocked_user_display_name: str
    created_at: datetime
    reason: str | None = None


class BlockedUserListResponse(BaseModel):
    items: list[BlockedUserResponse]
    total: int


class ThreadResponse(BaseModel):
    id: str
    contact_request_id: str
    post_id: str
    post_title: str
    counterpart_display_name: str
    status: ThreadStatus
    closed_by_user_id: str | None = None
    closed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ThreadListResponse(BaseModel):
    items: list[ThreadResponse]
    total: int


class ThreadMessageResponse(BaseModel):
    id: str
    thread_id: str
    sender_user_id: str
    sender_display_name: str
    body: str
    created_at: datetime


class ThreadMessageListResponse(BaseModel):
    items: list[ThreadMessageResponse]
    total: int


class SendThreadMessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str = Field(min_length=1, max_length=4000)


class CloseThreadResponse(BaseModel):
    thread: ThreadResponse
