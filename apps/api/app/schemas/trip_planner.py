from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Literal


TripStatus = Literal["draft", "active", "completed", "abandoned"]
TripConfidenceTier = Literal["declared", "active", "confirmed"]
TripVisibility = Literal["private", "link"]
TripWaypointKind = Literal["transit", "destination", "stopover"]
TripChecklistStatus = Literal["todo", "in_progress", "done", "skipped"]
TripChecklistOriginKind = Literal["manual", "route_template", "author_template"]
TripReminderChannel = Literal["telegram"]
TripReminderStatus = Literal["scheduled", "sent", "cancelled"]
TripAnnotationKind = Literal["note", "item_to_bring", "warning_ack"]
TripWarningSeverity = Literal["low", "medium", "high", "critical"]
TripExportFormat = Literal["json", "ics", "geojson"]


class TripCountryRef(BaseModel):
    id: str | None = None
    slug: str
    name: str
    iso2: str | None = None


class TripCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    scenario_slug: str | None = None
    origin_country_slug: str | None = None
    status: TripStatus = "draft"


class TripUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    scenario_slug: str | None = None
    origin_country_slug: str | None = None
    status: TripStatus | None = None
    confidence_tier: TripConfidenceTier | None = None


class TripWaypointCreateRequest(BaseModel):
    country_slug: str
    city: str | None = Field(default=None, max_length=120)
    kind: TripWaypointKind = "destination"
    planned_from: date | None = None
    planned_to: date | None = None
    notes: str | None = Field(default=None, max_length=2000)
    position: int | None = Field(default=None, ge=1)


class TripWaypointUpdateRequest(BaseModel):
    country_slug: str | None = None
    city: str | None = Field(default=None, max_length=120)
    kind: TripWaypointKind | None = None
    planned_from: date | None = None
    planned_to: date | None = None
    notes: str | None = Field(default=None, max_length=2000)
    position: int | None = Field(default=None, ge=1)


class TripWaypointReorderRequest(BaseModel):
    waypoint_ids: list[str] = Field(min_length=1)


class TripWaypoint(BaseModel):
    id: str
    position: int
    country: TripCountryRef
    city: str | None = None
    kind: TripWaypointKind
    planned_from: date | None = None
    planned_to: date | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class TripChecklistItemCreateRequest(BaseModel):
    waypoint_id: str | None = None
    title: str = Field(min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=4000)
    due_date: date | None = None
    status: TripChecklistStatus = "todo"
    position: int | None = Field(default=None, ge=1)


class TripChecklistItemUpdateRequest(BaseModel):
    waypoint_id: str | None = None
    title: str | None = Field(default=None, min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=4000)
    due_date: date | None = None
    status: TripChecklistStatus | None = None
    position: int | None = Field(default=None, ge=1)


class TripChecklistImportRequest(BaseModel):
    route_id: str


class TripChecklistItem(BaseModel):
    id: str
    waypoint_id: str | None = None
    title: str
    description: str | None = None
    due_date: date | None = None
    status: TripChecklistStatus
    origin_kind: TripChecklistOriginKind
    origin_ref: str | None = None
    position: int
    created_at: datetime
    updated_at: datetime


class TripReminderCreateRequest(BaseModel):
    checklist_item_id: str | None = None
    remind_at: datetime
    channel: TripReminderChannel = "telegram"


class TripReminder(BaseModel):
    id: str
    checklist_item_id: str | None = None
    checklist_item_title: str | None = None
    remind_at: datetime
    channel: TripReminderChannel
    status: TripReminderStatus
    sent_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TripAnnotationCreateRequest(BaseModel):
    waypoint_id: str | None = None
    kind: TripAnnotationKind
    body: str = Field(min_length=1, max_length=4000)
    position: int | None = Field(default=None, ge=1)


class TripAnnotationUpdateRequest(BaseModel):
    waypoint_id: str | None = None
    kind: TripAnnotationKind | None = None
    body: str | None = Field(default=None, min_length=1, max_length=4000)
    position: int | None = Field(default=None, ge=1)


class TripAnnotation(BaseModel):
    id: str
    waypoint_id: str | None = None
    kind: TripAnnotationKind
    body: str
    position: int | None = None
    created_at: datetime
    updated_at: datetime


class TripSummary(BaseModel):
    id: str
    title: str
    scenario_slug: str | None = None
    origin_country: TripCountryRef | None = None
    status: TripStatus
    confidence_tier: TripConfidenceTier
    visibility: TripVisibility
    share_token_prefix: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class TripDetail(TripSummary):
    waypoints: list[TripWaypoint] = Field(default_factory=list)
    checklist_items: list[TripChecklistItem] = Field(default_factory=list)
    reminders: list[TripReminder] = Field(default_factory=list)
    annotations: list[TripAnnotation] = Field(default_factory=list)


class TripListResponse(BaseModel):
    total: int
    items: list[TripSummary]


class TripDetailResponse(BaseModel):
    item: TripDetail


class TripWaypointListResponse(BaseModel):
    items: list[TripWaypoint]


class TripChecklistResponse(BaseModel):
    items: list[TripChecklistItem]


class TripReminderListResponse(BaseModel):
    items: list[TripReminder]


class TripAnnotationListResponse(BaseModel):
    items: list[TripAnnotation]


class TripShareResponse(BaseModel):
    trip_id: str
    token: str
    path: str
    visibility: TripVisibility


class TripWarning(BaseModel):
    code: str
    severity: TripWarningSeverity
    message: str
    source_ids: list[str] = Field(default_factory=list)
    origin_country_slug: str | None = None
    destination_country_slug: str | None = None
    waypoint_id: str | None = None


class TripWarningsResponse(BaseModel):
    trip_id: str
    methodology_version: str
    items: list[TripWarning]


class SharedTripWaypoint(BaseModel):
    position: int
    country: TripCountryRef
    city: str | None = None
    kind: TripWaypointKind
    planned_from: date | None = None
    planned_to: date | None = None


class SharedTripChecklistItem(BaseModel):
    title: str
    due_date: date | None = None
    status: TripChecklistStatus
    position: int


class SharedTripResponse(BaseModel):
    id: str
    title: str
    scenario_slug: str | None = None
    origin_country: TripCountryRef | None = None
    status: TripStatus
    confidence_tier: TripConfidenceTier
    waypoints: list[SharedTripWaypoint]
    checklist_items: list[SharedTripChecklistItem]
    updated_at: datetime


class TripCreateFromPassportRequest(BaseModel):
    token: str
    title: str | None = Field(default=None, min_length=1, max_length=200)


class TripWhatChangedCountry(BaseModel):
    country_slug: str
    total: int


class TripWhatChangedResponse(BaseModel):
    trip_id: str
    countries: list[TripWhatChangedCountry]
