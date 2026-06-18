from app.core.database import execute_one, fetch_all, fetch_one
from app.core.locales import SOURCE_LOCALE, localized_column, validate_locale
from app.schemas.decision_engine import UserStoryCreate
import json
from psycopg import Connection
from typing import Any


LEGAL_SIGNAL_SORT_COLUMNS = {
    "published_date": "ls.published_date",
    "effective_date": "ls.effective_date",
    "impact_level": "ls.impact_level",
    "created_at": "ls.created_at",
    "updated_at": "ls.updated_at",
}
COUNTRY_SOURCE_SORT_COLUMNS = {
    "title": "s.title",
    "created_at": "s.created_at",
    "published_at": "s.published_at",
    "last_checked_at": "s.last_checked_at",
    "confidence": "s.confidence",
}
USER_STORY_SORT_COLUMNS = {
    "created_at": "us.created_at",
    "year": "us.year",
    "satisfaction_score": "us.satisfaction_score",
}


def get_country_card(
    connection: Connection[Any], country_slug: str, locale: str
) -> dict[str, Any] | None:
    requested_locale = validate_locale(locale)
    row = fetch_one(
        connection,
        """
        SELECT
            cc.id,
            cc.country_id,
            cc.locale,
            cc.executive_summary,
            cc.migration_overview,
            cc.tax_overview,
            cc.cost_of_living_overview,
            cc.business_overview,
            cc.safety_overview,
            cc.legal_signals_summary,
            cc.risk_summary,
            cc.source_summary,
            cc.status,
            cc.created_at,
            cc.updated_at,
            cc.locale = %s AS is_translated,
            cc.locale AS resolved_locale,
            CASE WHEN cc.locale = 'en' THEN 'source' ELSE 'translated' END AS translation_status
        FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE c.slug = %s AND cc.locale = %s AND cc.status = 'published'
        """,
        (requested_locale, country_slug, requested_locale),
    )
    if row is not None:
        return row
    if requested_locale == SOURCE_LOCALE:
        return None
    return fetch_one(
        connection,
        """
        SELECT
            cc.id,
            cc.country_id,
            cc.locale,
            cc.executive_summary,
            cc.migration_overview,
            cc.tax_overview,
            cc.cost_of_living_overview,
            cc.business_overview,
            cc.safety_overview,
            cc.legal_signals_summary,
            cc.risk_summary,
            cc.source_summary,
            cc.status,
            cc.created_at,
            cc.updated_at,
            FALSE AS is_translated,
            'en' AS resolved_locale,
            'fallback' AS translation_status
        FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE c.slug = %s AND cc.locale = 'en' AND cc.status = 'published'
        """,
        (country_slug,),
    )


def get_scenario(
    connection: Connection[Any], slug: str, locale: str
) -> dict[str, Any] | None:
    requested_locale = validate_locale(locale)
    title_column = localized_column(requested_locale, "title_en", "title_ru")
    description_column = localized_column(
        requested_locale, "description_en", "description_ru"
    )
    if requested_locale == SOURCE_LOCALE:
        resolved_locale_sql = "'en'"
        status_sql = """
            CASE
                WHEN title_en IS NOT NULL OR description_en IS NOT NULL OR name IS NOT NULL THEN 'source'
                ELSE 'missing'
            END
        """
    else:
        resolved_locale_sql = """
            CASE
                WHEN title_ru IS NOT NULL AND description_ru IS NOT NULL THEN 'ru'
                ELSE 'en'
            END
        """
        status_sql = """
            CASE
                WHEN title_ru IS NOT NULL AND description_ru IS NOT NULL THEN 'translated'
                WHEN title_en IS NOT NULL OR description_en IS NOT NULL OR name IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END
        """
    return fetch_one(
        connection,
        f"""
        SELECT
            id,
            slug,
            COALESCE({title_column}, title_en, name, '') AS title,
            COALESCE({description_column}, description_en, description, '') AS description,
            weights,
            is_active,
            created_at,
            updated_at,
            {title_column} IS NOT NULL AND {description_column} IS NOT NULL AS is_translated,
            {resolved_locale_sql} AS resolved_locale,
            {status_sql} AS translation_status
        FROM scenarios
        WHERE slug = %s AND is_active = TRUE
        """,
        (slug,),
    )


def get_decision_scenario(
    connection: Connection[Any], slug: str, locale: str
) -> dict[str, Any] | None:
    return get_scenario(connection, slug, locale)


def list_decision_countries(
    connection: Connection[Any], country_slugs: list[str], locale: str
) -> list[dict[str, Any]]:
    if not country_slugs:
        return []
    requested_locale = validate_locale(locale)
    if requested_locale == SOURCE_LOCALE:
        resolved_locale_sql = "'en'"
        status_sql = "'source'"
    else:
        resolved_locale_sql = "'en'"
        status_sql = "'fallback'"
    return fetch_all(
        connection,
        f"""
        SELECT
            id::text AS id,
            slug,
            name,
            iso2 AS iso_code,
            {resolved_locale_sql} AS resolved_locale,
            {status_sql} AS translation_status
        FROM countries
        WHERE slug = ANY(%s) AND is_active = TRUE
        ORDER BY slug
        """,
        (country_slugs,),
    )


def list_decision_scores(
    connection: Connection[Any],
    scenario_slug: str,
    country_slugs: list[str],
    locale: str,
) -> list[dict[str, Any]]:
    if not country_slugs:
        return []
    requested_locale = validate_locale(locale)
    explanation_column = localized_column(
        requested_locale, "cs.explanation_en", "cs.explanation_ru"
    )
    if requested_locale == SOURCE_LOCALE:
        resolved_locale_sql = "'en'"
        status_sql = """
            CASE
                WHEN cs.explanation_en IS NOT NULL OR cs.summary IS NOT NULL THEN 'source'
                ELSE 'missing'
            END
        """
    else:
        resolved_locale_sql = """
            CASE
                WHEN cs.explanation_ru IS NOT NULL THEN 'ru'
                ELSE 'en'
            END
        """
        status_sql = """
            CASE
                WHEN cs.explanation_ru IS NOT NULL THEN 'translated'
                WHEN cs.explanation_en IS NOT NULL OR cs.summary IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END
        """
    return fetch_all(
        connection,
        f"""
        SELECT
            cs.id::text AS id,
            cs.country_id::text AS country_id,
            c.slug AS country_slug,
            s.slug AS scenario_slug,
            cs.score::float AS score,
            cs.score_label,
            COALESCE({explanation_column}, cs.explanation_en, cs.summary, '') AS explanation,
            cs.confidence,
            cs.calculated_at,
            {resolved_locale_sql} AS resolved_locale,
            {status_sql} AS translation_status
        FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios s ON s.id = cs.scenario_id
        WHERE s.slug = %s
          AND c.slug = ANY(%s)
        ORDER BY c.slug
        """,
        (scenario_slug, country_slugs),
    )


def list_decision_score_breakdowns(
    connection: Connection[Any], country_score_ids: list[str], locale: str
) -> list[dict[str, Any]]:
    if not country_score_ids:
        return []
    requested_locale = validate_locale(locale)
    explanation_column = localized_column(
        requested_locale, "explanation_en", "explanation_ru"
    )
    if requested_locale == SOURCE_LOCALE:
        resolved_locale_sql = "'en'"
        status_sql = "'source'"
    else:
        resolved_locale_sql = """
            CASE
                WHEN explanation_ru IS NOT NULL THEN 'ru'
                ELSE 'en'
            END
        """
        status_sql = """
            CASE
                WHEN explanation_ru IS NOT NULL THEN 'translated'
                WHEN explanation_en IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END
        """
    return fetch_all(
        connection,
        f"""
        SELECT
            country_score_id::text AS country_score_id,
            criterion,
            score::float AS score,
            weight::float AS weight,
            weighted_score::float AS weighted_score,
            COALESCE({explanation_column}, explanation_en, '') AS explanation,
            source_ids,
            confidence,
            {resolved_locale_sql} AS resolved_locale,
            {status_sql} AS translation_status
        FROM country_score_breakdowns
        WHERE country_score_id = ANY(%s::uuid[])
        ORDER BY criterion
        """,
        (country_score_ids,),
    )


def list_decision_legal_signals(
    connection: Connection[Any],
    country_slugs: list[str],
    locale: str,
) -> list[dict[str, Any]]:
    if not country_slugs:
        return []
    requested_locale = validate_locale(locale)
    title_column = localized_column(requested_locale, "ls.title_en", "ls.title_ru")
    summary_column = localized_column(
        requested_locale, "ls.summary_en", "ls.summary_ru"
    )
    if requested_locale == SOURCE_LOCALE:
        resolved_locale_sql = "'en'"
        status_sql = """
            CASE
                WHEN ls.title_en IS NOT NULL OR ls.summary_en IS NOT NULL OR ls.title IS NOT NULL THEN 'source'
                ELSE 'missing'
            END
        """
    else:
        resolved_locale_sql = """
            CASE
                WHEN ls.title_ru IS NOT NULL AND ls.summary_ru IS NOT NULL THEN 'ru'
                ELSE 'en'
            END
        """
        status_sql = """
            CASE
                WHEN ls.title_ru IS NOT NULL AND ls.summary_ru IS NOT NULL THEN 'translated'
                WHEN ls.title_en IS NOT NULL OR ls.summary_en IS NOT NULL OR ls.title IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END
        """
    return fetch_all(
        connection,
        f"""
        SELECT
            ls.id::text AS id,
            c.slug AS country_slug,
            COALESCE({title_column}, ls.title_en, ls.title, '') AS title,
            COALESCE({summary_column}, ls.summary_en, ls.summary, '') AS summary,
            ls.signal_type,
            ls.impact_direction,
            ls.impact_level,
            ls.source_id::text AS source_id,
            ls.confidence,
            {resolved_locale_sql} AS resolved_locale,
            {status_sql} AS translation_status
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE c.slug = ANY(%s)
          AND ls.status = 'published'
        ORDER BY
            CASE ls.impact_level
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                ELSE 4
            END,
            ls.published_date DESC NULLS LAST,
            ls.title
        LIMIT 50
        """,
        (country_slugs,),
    )


def list_decision_sources_by_ids(
    connection: Connection[Any], source_ids: list[str]
) -> list[dict[str, Any]]:
    unique_source_ids = sorted(set(source_ids))
    if not unique_source_ids:
        return []
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            COALESCE(url, '') AS url,
            source_type,
            confidence
        FROM sources
        WHERE id = ANY(%s::uuid[])
        ORDER BY title
        """,
        (unique_source_ids,),
    )


def list_scenario_countries(
    connection: Connection[Any], scenario_slug: str, locale: str
) -> list[dict[str, Any]]:
    requested_locale = validate_locale(locale)
    title_column = localized_column(requested_locale, "s.title_en", "s.title_ru")
    explanation_column = localized_column(
        requested_locale, "cs.explanation_en", "cs.explanation_ru"
    )
    if requested_locale == SOURCE_LOCALE:
        resolved_locale_sql = "'en'"
        status_sql = """
            CASE
                WHEN s.title_en IS NOT NULL OR cs.explanation_en IS NOT NULL OR s.name IS NOT NULL THEN 'source'
                ELSE 'missing'
            END
        """
    else:
        resolved_locale_sql = """
            CASE
                WHEN s.title_ru IS NOT NULL AND cs.explanation_ru IS NOT NULL THEN 'ru'
                ELSE 'en'
            END
        """
        status_sql = """
            CASE
                WHEN s.title_ru IS NOT NULL AND cs.explanation_ru IS NOT NULL THEN 'translated'
                WHEN s.title_en IS NOT NULL OR cs.explanation_en IS NOT NULL OR s.name IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END
        """
    return fetch_all(
        connection,
        f"""
        SELECT
            cs.id,
            cs.country_id,
            c.slug AS country_slug,
            c.name AS country_name,
            cs.scenario_id,
            s.slug AS scenario_slug,
            COALESCE({title_column}, s.title_en, s.name, '') AS scenario_name,
            cs.score::float AS score,
            COALESCE({explanation_column}, cs.explanation_en, cs.summary, '') AS explanation,
            cs.confidence,
            cs.calculated_at,
            {title_column} IS NOT NULL AND {explanation_column} IS NOT NULL AS is_translated,
            {resolved_locale_sql} AS resolved_locale,
            {status_sql} AS translation_status
        FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios s ON s.id = cs.scenario_id
        WHERE s.slug = %s
        ORDER BY cs.score DESC, c.slug
        """,
        (scenario_slug,),
    )


def list_score_breakdowns(
    connection: Connection[Any], country_score_ids: list[str]
) -> list[dict[str, Any]]:
    if not country_score_ids:
        return []
    return fetch_all(
        connection,
        """
        SELECT
            id,
            country_score_id,
            criterion,
            score::float AS score,
            weight::float AS weight,
            weighted_score::float AS weighted_score,
            explanation_en,
            explanation_ru,
            source_ids,
            confidence,
            created_at,
            updated_at
        FROM country_score_breakdowns
        WHERE country_score_id = ANY(%s::uuid[])
        ORDER BY criterion
        """,
        (country_score_ids,),
    )


def list_score_sources(
    connection: Connection[Any], country_slugs: list[str]
) -> list[dict[str, Any]]:
    if not country_slugs:
        return []
    return fetch_all(
        connection,
        """
        SELECT
            s.id,
            s.title,
            s.url,
            s.source_type,
            s.publisher,
            s.country_id,
            s.locale_id,
            s.reliability_level,
            s.published_at,
            s.accessed_at,
            s.created_at,
            s.updated_at
        FROM sources s
        JOIN countries c ON c.id = s.country_id
        WHERE c.slug = ANY(%s) AND s.status = 'published'
        ORDER BY c.slug, s.title
        """,
        (country_slugs,),
    )


def list_country_sources(
    connection: Connection[Any],
    country_slug: str,
    limit: int,
    offset: int,
    source_type: str | None = None,
    language: str | None = None,
    confidence: str | None = None,
    status: str = "published",
    sort: str = "title",
    order: str = "asc",
) -> list[dict[str, Any]]:
    filter_sql, params = _country_source_filters(
        country_slug, source_type, language, confidence, status
    )
    sort_column = COUNTRY_SOURCE_SORT_COLUMNS.get(
        sort, COUNTRY_SOURCE_SORT_COLUMNS["title"]
    )
    order_sql = "ASC" if order == "asc" else "DESC"
    return fetch_all(
        connection,
        f"""
        SELECT
            s.id,
            s.title,
            s.url,
            s.source_type,
            s.publisher,
            s.country_id,
            s.locale_id,
            s.reliability_level,
            s.language,
            s.confidence,
            s.status,
            s.published_at,
            s.accessed_at,
            s.last_checked_at,
            s.notes,
            s.created_at,
            s.updated_at
        FROM sources s
        JOIN countries c ON c.id = s.country_id
        WHERE {filter_sql}
        ORDER BY {sort_column} {order_sql} NULLS LAST, s.title
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )


def count_country_sources(
    connection: Connection[Any],
    country_slug: str,
    source_type: str | None = None,
    language: str | None = None,
    confidence: str | None = None,
    status: str = "published",
) -> int:
    filter_sql, params = _country_source_filters(
        country_slug, source_type, language, confidence, status
    )
    row = fetch_one(
        connection,
        f"""
        SELECT COUNT(*) AS total
        FROM sources s
        JOIN countries c ON c.id = s.country_id
        WHERE {filter_sql}
        """,
        params,
    )
    return int(row["total"]) if row else 0


def list_legal_signals(
    connection: Connection[Any],
    locale: str,
    country_slug: str | None,
    signal_type: str | None = None,
    impact_direction: str | None = None,
    impact_level: str | None = None,
    status: str = "published",
    limit: int = 20,
    offset: int = 0,
    sort: str = "published_date",
    order: str = "desc",
) -> list[dict[str, Any]]:
    requested_locale = validate_locale(locale)
    title_column = localized_column(requested_locale, "ls.title_en", "ls.title_ru")
    summary_column = localized_column(
        requested_locale, "ls.summary_en", "ls.summary_ru"
    )
    filter_sql, filter_params = _legal_signal_filters(
        country_slug, signal_type, impact_direction, impact_level, status
    )
    sort_column = LEGAL_SIGNAL_SORT_COLUMNS.get(
        sort, LEGAL_SIGNAL_SORT_COLUMNS["published_date"]
    )
    order_sql = "ASC" if order == "asc" else "DESC"
    if requested_locale == SOURCE_LOCALE:
        resolved_locale_sql = "'en'"
        status_sql = """
            CASE
                WHEN ls.title_en IS NOT NULL OR ls.summary_en IS NOT NULL OR ls.title IS NOT NULL THEN 'source'
                ELSE 'missing'
            END
        """
    else:
        resolved_locale_sql = """
            CASE
                WHEN ls.title_ru IS NOT NULL AND ls.summary_ru IS NOT NULL THEN 'ru'
                ELSE 'en'
            END
        """
        status_sql = """
            CASE
                WHEN ls.title_ru IS NOT NULL AND ls.summary_ru IS NOT NULL THEN 'translated'
                WHEN ls.title_en IS NOT NULL OR ls.summary_en IS NOT NULL OR ls.title IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END
        """
    return fetch_all(
        connection,
        f"""
        SELECT
            ls.id,
            ls.country_id,
            COALESCE({title_column}, ls.title_en, ls.title, '') AS title,
            COALESCE({summary_column}, ls.summary_en, ls.summary, '') AS summary,
            ls.signal_type,
            ls.impact_direction,
            ls.impact_level,
            ls.affected_groups,
            ls.published_date,
            ls.effective_date,
            ls.source_id,
            ls.confidence,
            ls.status,
            ls.created_at,
            ls.updated_at,
            {title_column} IS NOT NULL AND {summary_column} IS NOT NULL AS is_translated,
            {resolved_locale_sql} AS resolved_locale,
            {status_sql} AS translation_status
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE {filter_sql}
        ORDER BY {sort_column} {order_sql} NULLS LAST, ls.title
        LIMIT %s OFFSET %s
        """,
        (*filter_params, limit, offset),
    )


def count_legal_signals(
    connection: Connection[Any],
    country_slug: str | None = None,
    signal_type: str | None = None,
    impact_direction: str | None = None,
    impact_level: str | None = None,
    status: str = "published",
) -> int:
    filter_sql, params = _legal_signal_filters(
        country_slug, signal_type, impact_direction, impact_level, status
    )
    row = fetch_one(
        connection,
        f"""
        SELECT COUNT(*) AS total
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE {filter_sql}
        """,
        params,
    )
    return int(row["total"]) if row else 0


def get_legal_signal(
    connection: Connection[Any], signal_id: str, locale: str
) -> dict[str, Any] | None:
    requested_locale = validate_locale(locale)
    title_column = localized_column(requested_locale, "title_en", "title_ru")
    summary_column = localized_column(requested_locale, "summary_en", "summary_ru")
    if requested_locale == SOURCE_LOCALE:
        resolved_locale_sql = "'en'"
        status_sql = """
            CASE
                WHEN title_en IS NOT NULL OR summary_en IS NOT NULL OR title IS NOT NULL THEN 'source'
                ELSE 'missing'
            END
        """
    else:
        resolved_locale_sql = """
            CASE
                WHEN title_ru IS NOT NULL AND summary_ru IS NOT NULL THEN 'ru'
                ELSE 'en'
            END
        """
        status_sql = """
            CASE
                WHEN title_ru IS NOT NULL AND summary_ru IS NOT NULL THEN 'translated'
                WHEN title_en IS NOT NULL OR summary_en IS NOT NULL OR title IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END
        """
    return fetch_one(
        connection,
        f"""
        SELECT
            id,
            country_id,
            COALESCE({title_column}, title_en, title, '') AS title,
            COALESCE({summary_column}, summary_en, summary, '') AS summary,
            signal_type,
            impact_direction,
            impact_level,
            affected_groups,
            published_date,
            effective_date,
            source_id,
            confidence,
            status,
            created_at,
            updated_at,
            {title_column} IS NOT NULL AND {summary_column} IS NOT NULL AS is_translated,
            {resolved_locale_sql} AS resolved_locale,
            {status_sql} AS translation_status
        FROM legal_signals
        WHERE id::text = %s AND status = 'published'
        """,
        (signal_id,),
    )


def list_evidence_for_legal_signal(
    connection: Connection[Any], signal_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id,
            source_id,
            country_id,
            title,
            summary,
            url,
            quote,
            evidence_type,
            confidence_level,
            published_at,
            created_at,
            updated_at
        FROM evidence_items
        WHERE legal_signal_id::text = %s AND status = 'published'
        ORDER BY retrieved_at DESC NULLS LAST, title
        """,
        (signal_id,),
    )


def get_source(connection: Connection[Any], source_id: str) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            id,
            title,
            url,
            source_type,
            publisher,
            country_id,
            locale_id,
            reliability_level,
            language,
            confidence,
            status,
            published_at,
            accessed_at,
            last_checked_at,
            notes,
            created_at,
            updated_at
        FROM sources
        WHERE id::text = %s AND status = 'published'
        """,
        (source_id,),
    )


def list_evidence_for_source(
    connection: Connection[Any], source_id: str, limit: int, offset: int
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id,
            source_id,
            country_id,
            title,
            summary,
            url,
            quote,
            evidence_type,
            confidence_level,
            published_at,
            created_at,
            updated_at
        FROM evidence_items
        WHERE source_id::text = %s AND status = 'published'
        ORDER BY retrieved_at DESC NULLS LAST, title
        LIMIT %s OFFSET %s
        """,
        (source_id, limit, offset),
    )


def count_evidence_for_source(connection: Connection[Any], source_id: str) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS total
        FROM evidence_items
        WHERE source_id::text = %s AND status = 'published'
        """,
        (source_id,),
    )
    return int(row["total"]) if row else 0


def list_user_stories(
    connection: Connection[Any],
    limit: int,
    offset: int,
    origin_country_slug: str | None = None,
    destination_country_slug: str | None = None,
    scenario: str | None = None,
    verification_status: str | None = None,
    is_synthetic: bool | None = None,
    status: str = "published",
    sort: str = "created_at",
    order: str = "desc",
) -> list[dict[str, Any]]:
    filter_sql, params = _user_story_filters(
        origin_country_slug,
        destination_country_slug,
        scenario,
        verification_status,
        is_synthetic,
        status,
    )
    sort_column = USER_STORY_SORT_COLUMNS.get(
        sort, USER_STORY_SORT_COLUMNS["created_at"]
    )
    order_sql = "ASC" if order == "asc" else "DESC"
    return fetch_all(
        connection,
        f"""
        SELECT
            us.id,
            us.origin_country_id,
            us.destination_country_id,
            us.city,
            us.year,
            us.scenario,
            us.budget_initial_usd,
            us.budget_monthly_usd,
            us.legal_path,
            us.documents_used,
            us.problems,
            us.positive_outcome,
            us.negative_outcome,
            us.advice,
            us.satisfaction_score,
            us.verification_status,
            us.status,
            us.is_synthetic,
            us.notes,
            us.created_at,
            us.updated_at
        FROM user_stories us
        LEFT JOIN countries origin ON origin.id = us.origin_country_id
        JOIN countries destination ON destination.id = us.destination_country_id
        WHERE {filter_sql}
        ORDER BY {sort_column} {order_sql} NULLS LAST, us.id
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )


def count_user_stories(
    connection: Connection[Any],
    origin_country_slug: str | None = None,
    destination_country_slug: str | None = None,
    scenario: str | None = None,
    verification_status: str | None = None,
    is_synthetic: bool | None = None,
    status: str = "published",
) -> int:
    filter_sql, params = _user_story_filters(
        origin_country_slug,
        destination_country_slug,
        scenario,
        verification_status,
        is_synthetic,
        status,
    )
    row = fetch_one(
        connection,
        f"""
        SELECT COUNT(*) AS total
        FROM user_stories us
        LEFT JOIN countries origin ON origin.id = us.origin_country_id
        JOIN countries destination ON destination.id = us.destination_country_id
        WHERE {filter_sql}
        """,
        params,
    )
    return int(row["total"]) if row else 0


def _country_source_filters(
    country_slug: str,
    source_type: str | None,
    language: str | None,
    confidence: str | None,
    status: str,
) -> tuple[str, tuple[Any, ...]]:
    filters = ["c.slug = %s", "s.status = %s"]
    params: list[Any] = [country_slug, status]
    if source_type:
        filters.append("s.source_type = %s")
        params.append(source_type)
    if language:
        filters.append("s.language = %s")
        params.append(language)
    if confidence:
        filters.append("s.confidence = %s")
        params.append(confidence)
    return " AND ".join(filters), tuple(params)


def _legal_signal_filters(
    country_slug: str | None,
    signal_type: str | None,
    impact_direction: str | None,
    impact_level: str | None,
    status: str,
) -> tuple[str, tuple[Any, ...]]:
    filters = ["ls.status = %s"]
    params: list[Any] = [status]
    if country_slug:
        filters.append("c.slug = %s")
        params.append(country_slug)
    if signal_type:
        filters.append("ls.signal_type = %s")
        params.append(signal_type)
    if impact_direction:
        filters.append("ls.impact_direction = %s")
        params.append(impact_direction)
    if impact_level:
        filters.append("ls.impact_level = %s")
        params.append(impact_level)
    return " AND ".join(filters), tuple(params)


def _user_story_filters(
    origin_country_slug: str | None,
    destination_country_slug: str | None,
    scenario: str | None,
    verification_status: str | None,
    is_synthetic: bool | None,
    status: str,
) -> tuple[str, tuple[Any, ...]]:
    filters = ["us.status = %s"]
    params: list[Any] = [status]
    if origin_country_slug:
        filters.append("origin.slug = %s")
        params.append(origin_country_slug)
    if destination_country_slug:
        filters.append("destination.slug = %s")
        params.append(destination_country_slug)
    if scenario:
        filters.append("us.scenario = %s")
        params.append(scenario)
    if verification_status:
        filters.append("us.verification_status = %s")
        params.append(verification_status)
    if is_synthetic is not None:
        filters.append("us.is_synthetic = %s")
        params.append(is_synthetic)
    return " AND ".join(filters), tuple(params)


def get_user_story(connection: Connection[Any], story_id: str) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            id,
            origin_country_id,
            destination_country_id,
            city,
            year,
            scenario,
            budget_initial_usd,
            budget_monthly_usd,
            legal_path,
            documents_used,
            problems,
            positive_outcome,
            negative_outcome,
            advice,
            satisfaction_score,
            verification_status,
            status,
            is_synthetic,
            notes,
            created_at,
            updated_at
        FROM user_stories
        WHERE id::text = %s AND status = 'published'
        """,
        (story_id,),
    )


def create_user_story(
    connection: Connection[Any], payload: UserStoryCreate
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO user_stories (
            origin_country_id,
            destination_country_id,
            city,
            year,
            scenario,
            budget_initial_usd,
            budget_monthly_usd,
            legal_path,
            documents_used,
            problems,
            positive_outcome,
            negative_outcome,
            advice,
            satisfaction_score,
            verification_status,
            status,
            is_synthetic,
            notes
        )
        SELECT
            origin.id,
            destination.id,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s::jsonb,
            %s,
            %s,
            %s,
            %s,
            %s,
            CASE WHEN %s THEN 'synthetic' ELSE 'unverified' END,
            'draft',
            %s,
            %s
        FROM countries destination
        LEFT JOIN countries origin ON origin.slug = %s
        WHERE destination.slug = %s
        RETURNING
            id,
            origin_country_id,
            destination_country_id,
            city,
            year,
            scenario,
            budget_initial_usd,
            budget_monthly_usd,
            legal_path,
            documents_used,
            problems,
            positive_outcome,
            negative_outcome,
            advice,
            satisfaction_score,
            verification_status,
            status,
            is_synthetic,
            notes,
            created_at,
            updated_at
        """,
        (
            payload.city,
            payload.year,
            payload.scenario,
            payload.budget_initial_usd,
            payload.budget_monthly_usd,
            payload.legal_path,
            json.dumps(payload.documents_used),
            payload.problems,
            payload.positive_outcome,
            payload.negative_outcome,
            payload.advice,
            payload.satisfaction_score,
            payload.is_synthetic,
            payload.is_synthetic,
            payload.notes,
            payload.origin_country_slug,
            payload.destination_country_slug,
        ),
    )
