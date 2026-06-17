from app.core.database import fetch_one
from app.schemas.common import LocaleResolution, TranslationStatus, locale_resolution
from psycopg import Connection
from typing import Any


def row_has_translation(rows: list[dict[str, Any]]) -> bool:
    if not rows:
        return False
    return all(bool(row.get("is_translated")) for row in rows)


def build_locale(
    rows: list[dict[str, Any]], requested_locale: str, translatable: bool = True
) -> LocaleResolution:
    if not translatable:
        return locale_resolution(requested_locale, False, translatable=False)
    statuses = {
        status.value if isinstance(status, TranslationStatus) else status
        for status in (row.get("translation_status") for row in rows)
    }
    if TranslationStatus.fallback.value in statuses:
        return locale_resolution(requested_locale, False, has_fallback=True)
    if TranslationStatus.missing.value in statuses:
        return locale_resolution(requested_locale, False, has_fallback=False)
    if statuses == {TranslationStatus.exact.value}:
        return locale_resolution(requested_locale, True)
    return locale_resolution(requested_locale, row_has_translation(rows), bool(rows))


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
