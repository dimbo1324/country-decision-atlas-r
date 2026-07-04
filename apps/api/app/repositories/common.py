from app.core.database import fetch_one
from app.core.locales import SOURCE_LOCALE, validate_locale
from app.schemas.common import (
    LocaleResolution,
    TranslationStatus,
    locale_resolution,
)
from psycopg import Connection
from typing import Any


def _status_value(status: Any) -> str | None:
    if isinstance(status, TranslationStatus):
        return status.value
    if isinstance(status, str):
        return status
    return None


def build_locale(
    rows: list[dict[str, Any]], requested_locale: str
) -> LocaleResolution:
    locale = validate_locale(str(requested_locale))
    if not rows:
        return locale_resolution(
            locale, SOURCE_LOCALE, TranslationStatus.missing
        )
    if locale == SOURCE_LOCALE:
        return locale_resolution(
            locale, SOURCE_LOCALE, TranslationStatus.source
        )
    statuses = {
        status
        for status in (
            _status_value(row.get("translation_status")) for row in rows
        )
        if status
    }
    resolved_locales = {
        resolved
        for resolved in (row.get("resolved_locale") for row in rows)
        if isinstance(resolved, str)
    }
    if statuses == {TranslationStatus.translated.value}:
        return locale_resolution(locale, locale, TranslationStatus.translated)
    if statuses == {TranslationStatus.missing.value}:
        return locale_resolution(
            locale, SOURCE_LOCALE, TranslationStatus.missing
        )
    if TranslationStatus.translated.value in statuses and (
        TranslationStatus.fallback.value in statuses
        or TranslationStatus.missing.value in statuses
    ):
        return locale_resolution(locale, locale, TranslationStatus.fallback)
    if TranslationStatus.fallback.value in statuses:
        resolved_locale = (
            locale if locale in resolved_locales else SOURCE_LOCALE
        )
        return locale_resolution(
            locale, resolved_locale, TranslationStatus.fallback
        )
    if TranslationStatus.source.value in statuses:
        return locale_resolution(
            locale, SOURCE_LOCALE, TranslationStatus.fallback
        )
    return locale_resolution(locale, SOURCE_LOCALE, TranslationStatus.missing)


def require_country_id(connection: Connection[Any], country_id: str) -> str:
    row = fetch_one(
        connection,
        """
        SELECT id::text AS id
        FROM countries
        WHERE id::text = %s OR slug = %s
        """,
        (country_id, country_id),
    )
    if row is None:
        raise LookupError("Country not found.")
    return str(row["id"])
