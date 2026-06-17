from typing import Any, Literal
from pydantic import BaseModel, Field
LocaleCode = Literal["en", "ru"]
class LocaleResolution(BaseModel):
    requested_locale: str
    resolved_locale: str
    translation_status: Literal["source", "translated", "missing"]
class Pagination(BaseModel):
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
    total: int = Field(ge=0)
class ApiError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | list[Any] | None = None
class ErrorResponse(BaseModel):
    error: ApiError
def locale_resolution(requested_locale: str, has_translation: bool) -> LocaleResolution:
    if requested_locale == "en":
        return LocaleResolution(
            requested_locale=requested_locale,
            resolved_locale="en",
            translation_status="source",
        )
    if has_translation:
        return LocaleResolution(
            requested_locale=requested_locale,
            resolved_locale=requested_locale,
            translation_status="translated",
        )
    return LocaleResolution(
        requested_locale=requested_locale,
        resolved_locale="en",
        translation_status="missing",
    )
