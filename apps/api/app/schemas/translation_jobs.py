from app.schemas.common import Pagination
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Annotated, Any, Literal


class TranslationJobItem(BaseModel):
    id: str
    translation_unit_id: str | None = None
    source_locale_code: str | None = None
    target_locale_code: str | None = None
    status: str
    priority: int = 100
    attempts: int = 0
    max_attempts: int = 3
    provider: str | None = None
    provider_model: str | None = None
    error_message: str | None = None
    locked_at: datetime | None = None
    locked_by: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failed_at: datetime | None = None
    updated_at: datetime


class TranslationJobListResponse(BaseModel):
    items: list[TranslationJobItem]
    pagination: Pagination


class TranslationJobCreateMissingRequest(BaseModel):
    target_locale: Literal["en", "ru"]
    limit: int = Field(default=50, ge=1, le=500)
    priority: int = Field(default=100, ge=0, le=1000)


class TranslationJobCreateStaleRequest(BaseModel):
    target_locale: Literal["en", "ru"]
    limit: int = Field(default=50, ge=1, le=500)
    priority: int = Field(default=80, ge=0, le=1000)


class TranslationJobCreateResponse(BaseModel):
    created_count: int
    items: list[TranslationJobItem]


class TranslationJobProcessNextRequest(BaseModel):
    target_locale: Literal["en", "ru"] | None = None
    worker_id: Annotated[str, Field(min_length=1, max_length=100)] = "api-admin"
    dry_run: bool = False


class TranslationJobProcessBatchRequest(BaseModel):
    target_locale: Literal["en", "ru"] | None = None
    limit: int = Field(default=10, ge=1, le=100)
    worker_id: Annotated[str, Field(min_length=1, max_length=100)] = "api-admin"
    dry_run: bool = False


class TranslationJobRetryFailedRequest(BaseModel):
    target_locale: Literal["en", "ru"] | None = None
    limit: int = Field(default=50, ge=1, le=500)


class TranslationJobRetryFailedResponse(BaseModel):
    reset_count: int
    items: list[TranslationJobItem]


class TranslationJobProcessResult(BaseModel):
    job_id: str
    status: str
    target_locale_code: str | None = None
    variant_id: str | None = None
    translated_text: str | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None


class TranslationJobBatchResult(BaseModel):
    processed: int
    completed: int
    failed: int
    results: list[TranslationJobProcessResult]
