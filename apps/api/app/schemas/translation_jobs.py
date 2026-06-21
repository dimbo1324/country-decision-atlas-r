from app.schemas.common import Pagination
from datetime import datetime
from pydantic import BaseModel
from typing import Any


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
    target_locale: str
    limit: int = 50
    priority: int = 100


class TranslationJobCreateStaleRequest(BaseModel):
    target_locale: str
    limit: int = 50
    priority: int = 80


class TranslationJobCreateResponse(BaseModel):
    created_count: int
    items: list[TranslationJobItem]


class TranslationJobProcessNextRequest(BaseModel):
    target_locale: str | None = None
    worker_id: str = "api-admin"
    dry_run: bool = False


class TranslationJobProcessBatchRequest(BaseModel):
    target_locale: str | None = None
    limit: int = 10
    worker_id: str = "api-admin"
    dry_run: bool = False


class TranslationJobProcessResult(BaseModel):
    job_id: str
    status: str
    target_locale_code: str | None = None
    variant_id: str | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None


class TranslationJobBatchResult(BaseModel):
    processed: int
    completed: int
    failed: int
    results: list[TranslationJobProcessResult]
