from app.core.locales import validate_locale
from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Any


class LocaleCode(StrEnum):
    en = "en"
    ru = "ru"


class TranslationStatus(StrEnum):
    source = "source"
    translated = "translated"
    fallback = "fallback"
    missing = "missing"


class PublicationStatus(StrEnum):
    draft = "draft"
    review = "review"
    published = "published"
    archived = "archived"
    rejected = "rejected"


class LegalStatus(StrEnum):
    proposed = "proposed"
    adopted = "adopted"
    effective = "effective"
    expired = "expired"
    revoked = "revoked"
    unknown = "unknown"


class LocaleResolution(BaseModel):
    requested_locale: LocaleCode
    resolved_locale: LocaleCode
    translation_status: TranslationStatus


class Pagination(BaseModel):
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
    total: int = Field(ge=0)


class SortMeta(BaseModel):
    sort: str | None = None
    order: str = "asc"


class PaginatedMeta(BaseModel):
    pagination: Pagination
    sort: SortMeta | None = None


class ApiError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | list[Any] | None = None


class ErrorResponse(BaseModel):
    error: ApiError


class ContentValidationError(ErrorResponse):
    pass


class AdminRecomputeQueuedResponse(BaseModel):
    """Acknowledges that an all-countries recompute was requested. The
    request is only recorded, not executed inline; the actual recompute
    runs separately via the CLI recompute scripts, on a schedule or by
    hand."""

    queued: bool = True
    resource: str
    dry_run: bool
    event_id: str | None = None


def locale_resolution(
    requested_locale: str | LocaleCode,
    resolved_locale: str | LocaleCode,
    translation_status: str | TranslationStatus,
) -> LocaleResolution:
    requested = LocaleCode(validate_locale(str(requested_locale)))
    resolved = LocaleCode(validate_locale(str(resolved_locale)))
    status = TranslationStatus(translation_status)
    return LocaleResolution(
        requested_locale=requested,
        resolved_locale=resolved,
        translation_status=status,
    )


def source_locale_resolution(locale: str | LocaleCode) -> LocaleResolution:
    requested = validate_locale(str(locale))
    status = (
        TranslationStatus.source
        if requested == "en"
        else TranslationStatus.fallback
    )
    return locale_resolution(requested, "en", status)
