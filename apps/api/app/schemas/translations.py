from datetime import datetime
from uuid import UUID
from app.schemas.common import Pagination
from pydantic import BaseModel
class Translation(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    field_name: str
    locale_id: UUID
    translated_value: str
    status: str
    created_at: datetime
    updated_at: datetime
class TranslationListResponse(BaseModel):
    items: list[Translation]
    pagination: Pagination
class TranslationJob(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    source_locale_id: UUID | None = None
    target_locale_id: UUID
    status: str
    provider: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
class TranslationJobCreate(BaseModel):
    entity_type: str
    entity_id: UUID
    source_locale_code: str = "en"
    target_locale_code: str
    provider: str | None = None
class TranslationJobResponse(BaseModel):
    item: TranslationJob
