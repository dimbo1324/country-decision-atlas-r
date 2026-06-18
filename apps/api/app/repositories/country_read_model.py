from app.core.database import fetch_all, fetch_one
from app.core.locales import localized_column, validate_locale
from psycopg import Connection
from typing import Any


def get_country_read_model_country(
    connection: Connection[Any],
    country_slug: str,
    locale: str,
) -> dict[str, Any] | None:
    requested_locale = validate_locale(locale)
    return fetch_one(
        connection,
        """
        SELECT
            c.id::text AS id,
            c.slug,
            c.iso2 AS iso_code,
            COALESCE(t_name.translated_value, c.name, c.slug) AS name,
            c.region,
            CASE WHEN c.is_active THEN 'published' ELSE 'draft' END AS status,
            c.updated_at,
            CASE
                WHEN %s = 'en' THEN 'en'
                WHEN t_name.translated_value IS NOT NULL THEN %s
                ELSE 'en'
            END AS resolved_locale,
            CASE
                WHEN %s = 'en' THEN 'source'
                WHEN t_name.translated_value IS NOT NULL THEN 'translated'
                WHEN c.name IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END AS translation_status
        FROM countries c
        LEFT JOIN locales l ON l.code = %s
        LEFT JOIN translations t_name
            ON t_name.entity_type = 'country'
            AND t_name.entity_id = c.id
            AND t_name.field_name = 'name'
            AND t_name.locale_id = l.id
            AND t_name.status IN ('reviewed', 'approved')
        WHERE c.slug = %s
        """,
        (
            requested_locale,
            requested_locale,
            requested_locale,
            requested_locale,
            country_slug,
        ),
    )


def get_country_read_model_profile(
    connection: Connection[Any],
    country_slug: str,
    locale: str,
) -> dict[str, Any] | None:
    requested_locale = validate_locale(locale)
    row = fetch_one(
        connection,
        """
        SELECT
            cc.executive_summary,
            cc.migration_overview,
            cc.tax_overview,
            cc.cost_of_living_overview,
            cc.business_overview,
            cc.safety_overview,
            cc.legal_signals_summary,
            cc.risk_summary,
            cc.source_summary,
            cc.updated_at,
            cc.locale AS resolved_locale,
            CASE
                WHEN cc.locale = 'en' AND %s = 'en' THEN 'source'
                WHEN cc.locale = %s THEN 'translated'
                ELSE 'fallback'
            END AS translation_status
        FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE c.slug = %s
          AND cc.locale = %s
          AND cc.status = 'published'
        """,
        (
            requested_locale,
            requested_locale,
            country_slug,
            requested_locale,
        ),
    )
    if row is not None:
        return row
    return fetch_one(
        connection,
        """
        SELECT
            cc.executive_summary,
            cc.migration_overview,
            cc.tax_overview,
            cc.cost_of_living_overview,
            cc.business_overview,
            cc.safety_overview,
            cc.legal_signals_summary,
            cc.risk_summary,
            cc.source_summary,
            cc.updated_at,
            'en' AS resolved_locale,
            CASE WHEN %s = 'en' THEN 'source' ELSE 'fallback' END AS translation_status
        FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE c.slug = %s
          AND cc.locale = 'en'
          AND cc.status = 'published'
        """,
        (
            requested_locale,
            country_slug,
        ),
    )


def list_country_read_model_scores(
    connection: Connection[Any],
    country_slug: str,
    locale: str,
) -> list[dict[str, Any]]:
    requested_locale = validate_locale(locale)
    title_column = localized_column(requested_locale, "s.title_en", "s.title_ru")
    explanation_column = localized_column(
        requested_locale, "cs.explanation_en", "cs.explanation_ru"
    )
    return fetch_all(
        connection,
        f"""
        SELECT
            cs.id::text AS id,
            s.slug AS scenario_slug,
            COALESCE({title_column}, s.title_en, s.name, s.slug) AS scenario_title,
            cs.score::float AS score,
            cs.confidence,
            COALESCE({explanation_column}, cs.explanation_en, cs.summary, '')
                AS explanation,
            cs.calculated_at,
            cs.updated_at,
            CASE
                WHEN %s = 'en' THEN 'en'
                WHEN {title_column} IS NOT NULL
                  OR {explanation_column} IS NOT NULL THEN %s
                ELSE 'en'
            END AS resolved_locale,
            CASE
                WHEN %s = 'en' THEN 'source'
                WHEN {title_column} IS NOT NULL
                  AND {explanation_column} IS NOT NULL THEN 'translated'
                WHEN s.title_en IS NOT NULL
                  OR cs.explanation_en IS NOT NULL
                  OR s.name IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END AS translation_status
        FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios s ON s.id = cs.scenario_id
        WHERE c.slug = %s
          AND s.is_active = TRUE
          AND EXISTS (
              SELECT 1
              FROM country_score_breakdowns csb
              WHERE csb.country_score_id = cs.id
          )
        ORDER BY s.slug
        """,
        (
            requested_locale,
            requested_locale,
            requested_locale,
            country_slug,
        ),
    )


def list_country_read_model_score_breakdowns(
    connection: Connection[Any],
    country_score_ids: list[str],
    locale: str,
) -> list[dict[str, Any]]:
    if not country_score_ids:
        return []
    requested_locale = validate_locale(locale)
    explanation_column = localized_column(
        requested_locale, "explanation_en", "explanation_ru"
    )
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
            updated_at,
            CASE
                WHEN %s = 'en' THEN 'en'
                WHEN {explanation_column} IS NOT NULL THEN %s
                ELSE 'en'
            END AS resolved_locale,
            CASE
                WHEN %s = 'en' THEN 'source'
                WHEN {explanation_column} IS NOT NULL THEN 'translated'
                WHEN explanation_en IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END AS translation_status
        FROM country_score_breakdowns
        WHERE country_score_id = ANY(%s::uuid[])
        ORDER BY criterion
        """,
        (
            requested_locale,
            requested_locale,
            requested_locale,
            country_score_ids,
        ),
    )


def list_country_read_model_legal_signals(
    connection: Connection[Any],
    country_slug: str,
    locale: str,
    limit: int,
) -> list[dict[str, Any]]:
    requested_locale = validate_locale(locale)
    title_column = localized_column(requested_locale, "ls.title_en", "ls.title_ru")
    summary_column = localized_column(
        requested_locale, "ls.summary_en", "ls.summary_ru"
    )
    return fetch_all(
        connection,
        f"""
        SELECT
            ls.id::text AS id,
            COALESCE({title_column}, ls.title_en, ls.title, '') AS title,
            COALESCE({summary_column}, ls.summary_en, ls.summary, '') AS summary,
            ls.signal_type,
            ls.impact_direction,
            ls.impact_level,
            ls.affected_groups,
            ls.published_date,
            ls.effective_date,
            ls.confidence,
            ls.updated_at,
            CASE
                WHEN %s = 'en' THEN 'en'
                WHEN {title_column} IS NOT NULL
                  OR {summary_column} IS NOT NULL THEN %s
                ELSE 'en'
            END AS resolved_locale,
            CASE
                WHEN %s = 'en' THEN 'source'
                WHEN {title_column} IS NOT NULL
                  AND {summary_column} IS NOT NULL THEN 'translated'
                WHEN ls.title_en IS NOT NULL
                  OR ls.summary_en IS NOT NULL
                  OR ls.title IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END AS translation_status
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE c.slug = %s
          AND ls.status IN ('published', 'active')
        ORDER BY
            CASE ls.impact_level
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                ELSE 4
            END,
            ls.published_date DESC NULLS LAST,
            ls.title
        LIMIT %s
        """,
        (
            requested_locale,
            requested_locale,
            requested_locale,
            country_slug,
            limit,
        ),
    )


def list_country_read_model_sources(
    connection: Connection[Any],
    country_slug: str,
    limit: int,
) -> list[dict[str, Any]]:
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
            s.published_at,
            COALESCE(s.last_checked_at, s.accessed_at) AS last_checked_at,
            s.updated_at
        FROM sources s
        JOIN countries c ON c.id = s.country_id
        WHERE c.slug = %s
        ORDER BY
            CASE s.source_type
                WHEN 'official' THEN 1
                WHEN 'dataset' THEN 2
                WHEN 'expert' THEN 3
                WHEN 'research' THEN 4
                WHEN 'media' THEN 5
                ELSE 6
            END,
            s.title
        LIMIT %s
        """,
        (
            country_slug,
            limit,
        ),
    )


def get_country_read_model_evidence_summary(
    connection: Connection[Any],
    country_slug: str,
) -> dict[str, Any]:
    row = fetch_one(
        connection,
        """
        SELECT
            COUNT(*)::int AS total,
            COUNT(*) FILTER (WHERE COALESCE(ei.confidence, ei.confidence_level) = 'high')::int
                AS high_confidence,
            COUNT(*) FILTER (WHERE COALESCE(ei.confidence, ei.confidence_level) = 'medium')::int
                AS medium_confidence,
            COUNT(*) FILTER (WHERE COALESCE(ei.confidence, ei.confidence_level) = 'low')::int
                AS low_confidence
        FROM evidence_items ei
        JOIN countries c ON c.id = ei.country_id
        WHERE c.slug = %s
        """,
        (country_slug,),
    )
    return row or {
        "total": 0,
        "high_confidence": 0,
        "medium_confidence": 0,
        "low_confidence": 0,
    }


def get_country_read_model_user_stories_summary(
    connection: Connection[Any],
    country_slug: str,
) -> dict[str, Any]:
    row = fetch_one(
        connection,
        """
        SELECT
            COUNT(*)::int AS total,
            COUNT(*) FILTER (WHERE us.is_synthetic)::int AS synthetic,
            AVG(us.satisfaction_score)::float AS average_satisfaction_score
        FROM user_stories us
        LEFT JOIN countries origin ON origin.id = us.origin_country_id
        JOIN countries destination ON destination.id = us.destination_country_id
        WHERE origin.slug = %s OR destination.slug = %s
        """,
        (country_slug, country_slug),
    )
    return row or {
        "total": 0,
        "synthetic": 0,
        "average_satisfaction_score": None,
    }
