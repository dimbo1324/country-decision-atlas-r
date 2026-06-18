from app.core.database import fetch_all
from psycopg import Connection
from typing import Any


MVP_COUNTRY_SLUGS = ("russia", "uruguay")
MVP_SCENARIO_SLUGS = (
    "relocation_residence",
    "permanent_residence_citizenship",
    "low_budget_living",
    "business_self_employment",
    "safety_political_risk",
)


def list_missing_mvp_countries(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT expected.slug
        FROM unnest(%s::text[]) AS expected(slug)
        LEFT JOIN countries c
            ON c.slug = expected.slug
            AND c.is_active = TRUE
        WHERE c.id IS NULL
        ORDER BY expected.slug
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_published_countries_without_cards(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.id::text AS id,
            c.slug
        FROM countries c
        LEFT JOIN country_cards cc
            ON cc.country_id = c.id
            AND cc.locale = 'en'
            AND cc.status = 'published'
        WHERE c.slug = ANY(%s)
          AND c.is_active = TRUE
          AND cc.id IS NULL
        ORDER BY c.slug
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_published_countries_without_sources(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.id::text AS id,
            c.slug
        FROM countries c
        LEFT JOIN sources s
            ON s.country_id = c.id
            AND s.status = 'published'
        WHERE c.slug = ANY(%s)
          AND c.is_active = TRUE
        GROUP BY c.id, c.slug
        HAVING COUNT(s.id) = 0
        ORDER BY c.slug
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_missing_country_scores_for_required_scenarios(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            country_scope.slug AS country_slug,
            scenario_scope.slug AS scenario_slug
        FROM unnest(%s::text[]) AS country_scope(slug)
        CROSS JOIN unnest(%s::text[]) AS scenario_scope(slug)
        LEFT JOIN countries c
            ON c.slug = country_scope.slug
            AND c.is_active = TRUE
        LEFT JOIN scenarios s
            ON s.slug = scenario_scope.slug
            AND s.is_active = TRUE
        LEFT JOIN country_scores cs
            ON cs.country_id = c.id
            AND cs.scenario_id = s.id
        WHERE c.id IS NULL
           OR s.id IS NULL
           OR cs.id IS NULL
        ORDER BY country_scope.slug, scenario_scope.slug
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_scores_without_breakdowns(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cs.id::text AS country_score_id,
            c.slug AS country_slug,
            s.slug AS scenario_slug
        FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios s ON s.id = cs.scenario_id
        LEFT JOIN country_score_breakdowns csb
            ON csb.country_score_id = cs.id
        WHERE c.slug = ANY(%s)
          AND s.slug = ANY(%s)
        GROUP BY cs.id, c.slug, s.slug
        HAVING COUNT(csb.id) = 0
        ORDER BY c.slug, s.slug
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_scores_with_incomplete_breakdowns(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cs.id::text AS country_score_id,
            c.slug AS country_slug,
            s.slug AS scenario_slug,
            COUNT(csb.id)::int AS breakdown_count
        FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios s ON s.id = cs.scenario_id
        LEFT JOIN country_score_breakdowns csb
            ON csb.country_score_id = cs.id
        WHERE c.slug = ANY(%s)
          AND s.slug = ANY(%s)
        GROUP BY cs.id, c.slug, s.slug
        HAVING COUNT(csb.id) <> 7
        ORDER BY c.slug, s.slug
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_scores_with_invalid_weight_sum(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cs.id::text AS country_score_id,
            c.slug AS country_slug,
            s.slug AS scenario_slug,
            COALESCE(SUM(csb.weight), 0)::float AS weight_sum
        FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios s ON s.id = cs.scenario_id
        LEFT JOIN country_score_breakdowns csb
            ON csb.country_score_id = cs.id
        WHERE c.slug = ANY(%s)
          AND s.slug = ANY(%s)
        GROUP BY cs.id, c.slug, s.slug
        HAVING ABS(COALESCE(SUM(csb.weight), 0) - 1.0) > 0.001
        ORDER BY c.slug, s.slug
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_published_legal_signals_without_source(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            country_id::text AS country_id
        FROM legal_signals
        WHERE status = 'published'
          AND source_id IS NULL
        ORDER BY title
        """,
    )


def list_published_legal_signals_without_evidence(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            ls.id::text AS id,
            ls.title,
            ls.country_id::text AS country_id
        FROM legal_signals ls
        LEFT JOIN evidence_items e
            ON e.legal_signal_id = ls.id
            AND e.status = 'published'
        WHERE ls.status = 'published'
        GROUP BY ls.id, ls.title, ls.country_id
        HAVING COUNT(e.id) = 0
        ORDER BY ls.title
        """,
    )


def list_evidence_without_source(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            claim
        FROM evidence_items
        WHERE source_id IS NULL
        ORDER BY id
        """,
    )


def list_evidence_without_country(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            claim
        FROM evidence_items
        WHERE country_id IS NULL
        ORDER BY id
        """,
    )


def list_published_sources_with_missing_required_fields(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            CASE
                WHEN title IS NULL OR title = '' THEN 'title'
                WHEN url IS NULL OR url = '' THEN 'url'
                WHEN publisher IS NULL OR publisher = '' THEN 'publisher'
                WHEN source_type IS NULL OR source_type = '' THEN 'source_type'
                WHEN COALESCE(confidence, reliability_level) IS NULL THEN 'confidence'
                ELSE 'unknown'
            END AS missing_field
        FROM sources
        WHERE status = 'published'
          AND (
              title IS NULL
              OR title = ''
              OR url IS NULL
              OR url = ''
              OR publisher IS NULL
              OR publisher = ''
              OR source_type IS NULL
              OR source_type = ''
              OR COALESCE(confidence, reliability_level) IS NULL
          )
        ORDER BY title
        """,
    )


def list_invalid_synthetic_user_stories(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            verification_status,
            is_synthetic,
            notes
        FROM user_stories
        WHERE is_synthetic = TRUE
          AND (
              verification_status = 'verified'
              OR notes IS NULL
              OR notes = ''
              OR (
                  LOWER(notes) NOT LIKE '%synthetic%'
                  AND LOWER(notes) NOT LIKE '%demo%'
              )
          )
        ORDER BY created_at DESC
        """,
    )


def list_country_cards_with_empty_major_sections(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cc.id::text AS id,
            c.slug AS country_slug,
            cc.locale
        FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE c.slug = ANY(%s)
          AND cc.status = 'published'
          AND (
              COALESCE(cc.executive_summary, '') = ''
              OR COALESCE(cc.migration_overview, '') = ''
              OR COALESCE(cc.tax_overview, '') = ''
              OR COALESCE(cc.cost_of_living_overview, '') = ''
              OR COALESCE(cc.business_overview, '') = ''
              OR COALESCE(cc.safety_overview, '') = ''
              OR COALESCE(cc.legal_signals_summary, '') = ''
              OR COALESCE(cc.risk_summary, '') = ''
              OR COALESCE(cc.source_summary, '') = ''
          )
        ORDER BY c.slug, cc.locale
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )
