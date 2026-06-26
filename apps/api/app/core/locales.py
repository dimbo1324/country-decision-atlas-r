from app.core.errors import api_error
from fastapi import Depends, Query
from typing import Annotated, Literal


SupportedLocale = Literal["en", "ru"]

SUPPORTED_LOCALES: tuple[SupportedLocale, ...] = ("en", "ru")
DEFAULT_LOCALE: SupportedLocale = "ru"
AUTHORING_LOCALE: SupportedLocale = "ru"
DEFAULT_CONTENT_LOCALE: SupportedLocale = AUTHORING_LOCALE
LEGACY_SOURCE_LOCALE: SupportedLocale = "en"
SOURCE_LOCALE: SupportedLocale = LEGACY_SOURCE_LOCALE


def validate_locale(locale: str | None = None) -> SupportedLocale:
    candidate = locale or DEFAULT_LOCALE
    if candidate in SUPPORTED_LOCALES:
        return candidate
    raise api_error(
        422,
        "unsupported_locale",
        "Unsupported locale.",
        {
            "requested_locale": candidate,
            "supported_locales": list(SUPPORTED_LOCALES),
        },
    )


def get_locale(
    locale: Annotated[
        str,
        Query(
            pattern="^[a-z]{2}$",
            json_schema_extra={"enum": list(SUPPORTED_LOCALES)},
        ),
    ] = DEFAULT_LOCALE,
) -> SupportedLocale:
    return validate_locale(locale)


LocaleQuery = Annotated[SupportedLocale, Depends(get_locale)]


def localized_column(locale: str, en_column: str, ru_column: str) -> str:
    if validate_locale(locale) == "ru":
        return ru_column
    return en_column
