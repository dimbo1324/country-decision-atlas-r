from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


Polarity = str
License = str
Visibility = str
DefinitionStatus = str


class AuthorRef(BaseModel):
    user_id: str
    display_name: str


class AuthorMetricDefinitionBase(BaseModel):
    id: str
    slug: str
    name_en: str
    name_ru: str
    methodology_en: str
    methodology_ru: str
    polarity: Polarity
    scale_min: float
    scale_max: float
    license: License
    author: AuthorRef
    forked_from_id: str | None = None
    version: int
    published_at: datetime | None = None


class MyAuthorMetricDefinition(AuthorMetricDefinitionBase):
    status: DefinitionStatus
    visibility: Visibility
    created_at: datetime
    updated_at: datetime
    submitted_at: datetime | None = None
    archived_at: datetime | None = None
    rejected_at: datetime | None = None
    moderation_reason: str | None = None


class AdminAuthorMetricDefinition(MyAuthorMetricDefinition):
    author_user_id: str
    moderated_by: str | None = None
    moderated_at: datetime | None = None


class PublicAuthorMetricListResponse(BaseModel):
    items: list[AuthorMetricDefinitionBase]
    total: int


class MyAuthorMetricListResponse(BaseModel):
    items: list[MyAuthorMetricDefinition]
    total: int


class AdminAuthorMetricListResponse(BaseModel):
    items: list[AdminAuthorMetricDefinition]
    total: int


class CreateAuthorMetricRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str = Field(min_length=2, max_length=64)
    name_en: str = Field(min_length=3, max_length=140)
    name_ru: str = Field(min_length=3, max_length=140)
    methodology_en: str = Field(default="", max_length=4000)
    methodology_ru: str = Field(default="", max_length=4000)
    polarity: Polarity = "higher_is_better"
    scale_min: float = 0
    scale_max: float = 100
    license: License = "platform"
    visibility: Visibility = "private"


class UpdateAuthorMetricRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name_en: str | None = Field(default=None, min_length=3, max_length=140)
    name_ru: str | None = Field(default=None, min_length=3, max_length=140)
    methodology_en: str | None = Field(default=None, max_length=4000)
    methodology_ru: str | None = Field(default=None, max_length=4000)
    polarity: Polarity | None = None
    scale_min: float | None = None
    scale_max: float | None = None
    license: License | None = None
    visibility: Visibility | None = None


class SubmitAuthorMetricResponse(BaseModel):
    definition: MyAuthorMetricDefinition


class ArchiveAuthorMetricResponse(BaseModel):
    definition: MyAuthorMetricDefinition


class ForkAuthorMetricRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str = Field(min_length=2, max_length=64)


class ModerateAuthorMetricRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    moderation_reason: str | None = Field(default=None, max_length=1000)


class ModerateAuthorMetricResponse(BaseModel):
    definition: AdminAuthorMetricDefinition


class AuthorMetricValueItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    country_slug: str
    value: float
    source_url: str | None = None
    is_personal_experience: bool = False
    note: str | None = Field(default=None, max_length=1000)
    valid_as_of: date | None = None


class BulkUpsertAuthorMetricValuesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AuthorMetricValueItem] = Field(min_length=1, max_length=300)


class AuthorMetricValueResponse(BaseModel):
    country_id: str
    country_slug: str
    country_name: str
    value: float
    source_url: str | None = None
    is_personal_experience: bool
    note: str | None = None
    valid_as_of: date | None = None
    updated_at: datetime


class AuthorMetricValueListResponse(BaseModel):
    items: list[AuthorMetricValueResponse]
    total: int


class CreateSubscriptionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric_id: str | None = None
    author_user_id: str | None = None


class SubscriptionResponse(BaseModel):
    id: str
    metric_id: str | None = None
    metric_slug: str | None = None
    metric_name_en: str | None = None
    author_user_id: str | None = None
    author_display_name: str | None = None
    created_at: datetime


class SubscriptionListResponse(BaseModel):
    items: list[SubscriptionResponse]
    total: int


class FeedEntryResponse(BaseModel):
    metric_id: str
    metric_slug: str
    metric_name_en: str
    metric_name_ru: str
    author: AuthorRef
    country_id: str
    country_slug: str
    country_name: str
    value: float
    value_updated_at: datetime


class SubscriptionFeedResponse(BaseModel):
    items: list[FeedEntryResponse]
    total: int


class CountryAuthorMetricEntry(AuthorMetricDefinitionBase):
    value: float
    source_url: str | None = None
    is_personal_experience: bool
    note: str | None = None
    valid_as_of: date | None = None
    value_updated_at: datetime


class CountryAuthorMetricsResponse(BaseModel):
    country_slug: str
    items: list[CountryAuthorMetricEntry]
    total: int


class AuthorReputationResponse(BaseModel):
    author_user_id: str
    coverage_score: float
    freshness_score: float
    sourcing_score: float
    subscriber_count: int
    published_metric_count: int
    computed_at: datetime
    methodology_version: str
