from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


def list_glossary_terms(
    connection: Connection[Any],
    locale: str = "en",
    category: str | None = None,
    query: str | None = None,
) -> list[dict[str, Any]]:
    use_ru = locale == "ru"
    params: list[Any] = [use_ru, use_ru]
    filters = ["status = 'published'"]
    if category:
        filters.append("category = %s")
        params.append(category)
    if query:
        filters.append("(LOWER(term) LIKE %s OR LOWER(term_ru) LIKE %s)")
        like = f"%{query.lower()}%"
        params.extend([like, like])
    where = " AND ".join(filters)
    return fetch_all(
        connection,
        f"""
        SELECT
            slug,
            CASE WHEN %s THEN term_ru ELSE term END AS term,
            CASE WHEN %s THEN definition_ru ELSE definition END AS definition,
            category,
            related_terms,
            display_order,
            updated_at
        FROM glossary_terms
        WHERE {where}
        ORDER BY display_order ASC
        """,
        params,
    )


def get_glossary_term(
    connection: Connection[Any], slug: str, locale: str = "en"
) -> dict[str, Any] | None:
    use_ru = locale == "ru"
    return fetch_one(
        connection,
        """
        SELECT
            slug,
            CASE WHEN %s THEN term_ru ELSE term END AS term,
            CASE WHEN %s THEN definition_ru ELSE definition END AS definition,
            category,
            related_terms,
            display_order,
            updated_at
        FROM glossary_terms
        WHERE slug = %s
          AND status = 'published'
        """,
        (use_ru, use_ru, slug),
    )
