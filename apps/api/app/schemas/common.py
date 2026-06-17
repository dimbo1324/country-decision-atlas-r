from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Any


class LocaleCode(StrEnum):
    en = "en"
    ru = "ru"


class TranslationStatus(StrEnum):
    exact = "exact"
    fallback = "fallback"
    missing = "missing"
    not_applicable = "not_applicable"


SUPPORTED_LOCALES = frozenset(locale.value for locale in LocaleCode)


class LocaleResolution(BaseModel):
    requested_locale: LocaleCode
    resolved_locale: LocaleCode
    translation_status: TranslationStatus


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


def validate_locale(locale: str | LocaleCode) -> LocaleCode:
    try:
        return LocaleCode(locale)
    except ValueError as error:
        raise ValueError(f"Unsupported locale: {locale}") from error


def localized_column(locale: str | LocaleCode, en_column: str, ru_column: str) -> str:
    supported_locale = validate_locale(locale)
    if supported_locale == LocaleCode.ru:
        return ru_column
    return en_column


def locale_resolution(
    requested_locale: str | LocaleCode,
    has_translation: bool,
    has_fallback: bool = True,
    translatable: bool = True,
) -> LocaleResolution:
    locale = validate_locale(requested_locale)
    if not translatable:
        return LocaleResolution(
            requested_locale=locale,
            resolved_locale=locale,
            translation_status=TranslationStatus.not_applicable,
        )
    if locale == LocaleCode.en and has_fallback:
        return LocaleResolution(
            requested_locale=locale,
            resolved_locale=LocaleCode.en,
            translation_status=TranslationStatus.exact,
        )
    if has_translation:
        return LocaleResolution(
            requested_locale=locale,
            resolved_locale=locale,
            translation_status=TranslationStatus.exact,
        )
    if has_fallback:
        return LocaleResolution(
            requested_locale=locale,
            resolved_locale=LocaleCode.en,
            translation_status=TranslationStatus.fallback,
        )
    return LocaleResolution(
        requested_locale=locale,
        resolved_locale=LocaleCode.en,
        translation_status=TranslationStatus.missing,
    )
