from app.core.database import execute_one, fetch_all, fetch_one
from app.core.locales import validate_locale
from psycopg import Connection
from typing import Any


ROUTE_PUBLIC_FIELDS = """
    r.id::text AS id,
    r.country_id::text AS country_id,
    c.slug AS country_slug,
    COALESCE(c.name, c.slug) AS country_name,
    r.route_type,
    r.slug,
    CASE WHEN %s = 'ru' THEN COALESCE(r.title_ru, r.title) ELSE r.title END AS title,
    CASE WHEN %s = 'ru' THEN COALESCE(r.summary_ru, r.summary) ELSE r.summary END AS summary,
    CASE
        WHEN %s = 'ru' THEN COALESCE(r.eligibility_summary_ru, r.eligibility_summary)
        ELSE r.eligibility_summary
    END AS eligibility_summary,
    CASE
        WHEN %s = 'ru' THEN COALESCE(r.income_requirement_note_ru, r.income_requirement_note)
        ELSE r.income_requirement_note
    END AS income_requirement_note,
    CASE WHEN %s = 'ru' THEN COALESCE(r.fees_note_ru, r.fees_note) ELSE r.fees_note END
        AS fees_note,
    CASE
        WHEN %s = 'ru' THEN COALESCE(r.processing_time_note_ru, r.processing_time_note)
        ELSE r.processing_time_note
    END AS processing_time_note,
    CASE WHEN %s = 'ru' THEN COALESCE(r.stay_period_note_ru, r.stay_period_note) ELSE r.stay_period_note END
        AS stay_period_note,
    CASE WHEN %s = 'ru' THEN COALESCE(r.renewal_note_ru, r.renewal_note) ELSE r.renewal_note END
        AS renewal_note,
    CASE WHEN %s = 'ru' THEN COALESCE(r.tax_warning_ru, r.tax_warning) ELSE r.tax_warning END
        AS tax_warning,
    CASE WHEN %s = 'ru' THEN COALESCE(r.legal_warning_ru, r.legal_warning) ELSE r.legal_warning END
        AS legal_warning,
    r.allows_work,
    r.allows_family,
    r.leads_to_pr,
    r.leads_to_citizenship,
    r.requires_income_proof,
    r.requires_local_address,
    r.requires_criminal_record_check,
    r.legal_status,
    r.status,
    r.created_at,
    r.updated_at
"""

ADMIN_ROUTE_FIELDS = """
    id::text AS id,
    country_id::text AS country_id,
    route_type,
    slug,
    title,
    title_ru,
    summary,
    summary_ru,
    eligibility_summary,
    eligibility_summary_ru,
    income_requirement_note,
    income_requirement_note_ru,
    fees_note,
    fees_note_ru,
    processing_time_note,
    processing_time_note_ru,
    stay_period_note,
    stay_period_note_ru,
    renewal_note,
    renewal_note_ru,
    tax_warning,
    tax_warning_ru,
    legal_warning,
    legal_warning_ru,
    allows_work,
    allows_family,
    leads_to_pr,
    leads_to_citizenship,
    requires_income_proof,
    requires_local_address,
    requires_criminal_record_check,
    status,
    legal_status,
    created_at,
    updated_at
"""


def list_routes_by_country(
    connection: Connection[Any],
    country_slug: str,
    locale: str,
    route_type: str | None = None,
    allows_work: str | None = None,
    allows_family: str | None = None,
    leads_to_pr: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    requested_locale = validate_locale(locale)
    where_sql, params = _build_route_filters(
        country_slug, route_type, allows_work, allows_family, leads_to_pr
    )
    return fetch_all(
        connection,
        f"""
        SELECT
            {ROUTE_PUBLIC_FIELDS}
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        WHERE {where_sql}
        ORDER BY r.route_type, r.title
        LIMIT %s OFFSET %s
        """,
        (
            *([requested_locale] * 10),
            *params,
            limit,
            offset,
        ),
    )


def count_routes_by_country(
    connection: Connection[Any],
    country_slug: str,
    route_type: str | None = None,
    allows_work: str | None = None,
    allows_family: str | None = None,
    leads_to_pr: str | None = None,
) -> int:
    where_sql, params = _build_route_filters(
        country_slug, route_type, allows_work, allows_family, leads_to_pr
    )
    row = fetch_one(
        connection,
        f"""
        SELECT COUNT(*) AS total
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        WHERE {where_sql}
        """,
        params,
    )
    return int(row["total"]) if row else 0


def get_route_by_id(
    connection: Connection[Any],
    route_id: str,
    locale: str,
) -> dict[str, Any] | None:
    requested_locale = validate_locale(locale)
    return fetch_one(
        connection,
        f"""
        SELECT
            {ROUTE_PUBLIC_FIELDS}
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        WHERE r.id::text = %s
          AND r.status = 'published'
        """,
        (
            *([requested_locale] * 10),
            route_id,
        ),
    )


def get_route_by_slug(
    connection: Connection[Any],
    country_slug: str,
    route_slug: str,
    locale: str,
) -> dict[str, Any] | None:
    requested_locale = validate_locale(locale)
    return fetch_one(
        connection,
        f"""
        SELECT
            {ROUTE_PUBLIC_FIELDS}
        FROM routes r
        JOIN countries c ON c.id = r.country_id
        WHERE c.slug = %s
          AND r.slug = %s
          AND r.status = 'published'
        """,
        (
            *([requested_locale] * 10),
            country_slug,
            route_slug,
        ),
    )


def list_route_documents(
    connection: Connection[Any],
    route_id: str,
    locale: str,
) -> list[dict[str, Any]]:
    requested_locale = validate_locale(locale)
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            route_id::text AS route_id,
            CASE WHEN %s = 'ru' THEN COALESCE(name_ru, name) ELSE name END AS name,
            is_mandatory,
            CASE WHEN %s = 'ru' THEN COALESCE(note_ru, note) ELSE note END AS note,
            display_order
        FROM route_documents
        WHERE route_id::text = %s
        ORDER BY display_order ASC, name ASC
        """,
        (
            requested_locale,
            requested_locale,
            route_id,
        ),
    )


def list_route_sources(
    connection: Connection[Any],
    route_id: str,
    locale: str,
) -> list[dict[str, Any]]:
    validate_locale(locale)
    return fetch_all(
        connection,
        """
        SELECT
            s.id::text AS id,
            s.title,
            s.url,
            s.source_type,
            s.publisher,
            COALESCE(s.confidence, s.reliability_level) AS confidence,
            c.slug AS country_slug
        FROM route_sources rs
        JOIN sources s ON s.id = rs.source_id
        LEFT JOIN countries c ON c.id = s.country_id
        WHERE rs.route_id::text = %s
          AND s.status = 'published'
        ORDER BY
            CASE s.source_type
                WHEN 'official' THEN 1
                WHEN 'dataset' THEN 2
                WHEN 'research' THEN 3
                ELSE 4
            END,
            s.title
        """,
        (route_id,),
    )


def list_route_evidence(
    connection: Connection[Any],
    route_id: str,
    locale: str,
) -> list[dict[str, Any]]:
    validate_locale(locale)
    return fetch_all(
        connection,
        """
        SELECT
            ei.id::text AS id,
            ei.source_id::text AS source_id,
            COALESCE(ei.claim, ei.title) AS claim,
            COALESCE(ei.excerpt, ei.summary) AS excerpt,
            COALESCE(ei.confidence, ei.confidence_level) AS confidence,
            c.slug AS country_slug,
            s.title AS source_title,
            s.url AS source_url
        FROM route_evidence re
        JOIN evidence_items ei ON ei.id = re.evidence_item_id
        LEFT JOIN sources s ON s.id = ei.source_id
        LEFT JOIN countries c ON c.id = ei.country_id
        WHERE re.route_id::text = %s
          AND ei.status = 'published'
        ORDER BY COALESCE(ei.retrieved_at, ei.created_at) DESC NULLS LAST, ei.title
        """,
        (route_id,),
    )


def get_route_for_admin(
    connection: Connection[Any],
    route_id: str,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {ADMIN_ROUTE_FIELDS}
        FROM routes
        WHERE id::text = %s
        """,
        (route_id,),
    )


def patch_route_status(
    connection: Connection[Any],
    route_id: str,
    new_status: str,
) -> dict[str, Any]:
    return execute_one(
        connection,
        f"""
        UPDATE routes
        SET
            status = %s,
            updated_at = NOW()
        WHERE id::text = %s
        RETURNING
            {ADMIN_ROUTE_FIELDS}
        """,
        (
            new_status,
            route_id,
        ),
    )


def get_country_slug_by_id(
    connection: Connection[Any],
    country_id: str,
) -> str | None:
    row = fetch_one(
        connection,
        """
        SELECT slug
        FROM countries
        WHERE id::text = %s
        """,
        (country_id,),
    )
    return str(row["slug"]) if row else None


def _build_route_filters(
    country_slug: str,
    route_type: str | None,
    allows_work: str | None,
    allows_family: str | None,
    leads_to_pr: str | None,
) -> tuple[str, tuple[Any, ...]]:
    filters = ["c.slug = %s", "r.status = 'published'"]
    params: list[Any] = [country_slug]
    if route_type:
        filters.append("r.route_type = %s")
        params.append(route_type)
    if allows_work:
        filters.append("r.allows_work = %s")
        params.append(allows_work)
    if allows_family:
        filters.append("r.allows_family = %s")
        params.append(allows_family)
    if leads_to_pr:
        filters.append("r.leads_to_pr = %s")
        params.append(leads_to_pr)
    return " AND ".join(filters), tuple(params)
