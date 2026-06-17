from typing import Any

from app.core.database import fetch_one
from app.schemas.common import LocaleResolution, locale_resolution
from psycopg import Connection


def row_has_translation(rows: list[dict[str, Any]]) -> bool:
    if not rows:
        return False
    return all(bool(row.get("is_translated")) for row in rows)


def build_locale(rows: list[dict[str, Any]], requested_locale: str) -> LocaleResolution:
    return locale_resolution(requested_locale, row_has_translation(rows))


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
