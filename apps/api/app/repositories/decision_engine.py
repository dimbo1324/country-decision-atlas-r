from app.core.database import execute_one, fetch_all, fetch_one
from app.schemas.common import LocaleCode, localized_column, validate_locale
from app.schemas.decision_engine import UserStoryCreate
import json
from psycopg import Connection
from typing import Any


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
            'exact' AS translation_status
        FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE c.slug = %s AND cc.locale = %s
        """,
        (requested_locale.value, country_slug, requested_locale.value),
    )
    if row is not None:
        return row
    if requested_locale == LocaleCode.en:
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
            'fallback' AS translation_status
        FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE c.slug = %s AND cc.locale = 'en'
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
            CASE
                WHEN {title_column} IS NOT NULL AND {description_column} IS NOT NULL THEN 'exact'
                WHEN title_en IS NOT NULL OR description_en IS NOT NULL OR name IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END AS translation_status
        FROM scenarios
        WHERE slug = %s AND is_active = TRUE
        """,
        (slug,),
    )


def list_scenario_countries(
    connection: Connection[Any], scenario_slug: str, locale: str
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
            CASE
                WHEN {title_column} IS NOT NULL AND {explanation_column} IS NOT NULL THEN 'exact'
                WHEN s.title_en IS NOT NULL OR cs.explanation_en IS NOT NULL OR s.name IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END AS translation_status
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
        WHERE c.slug = ANY(%s)
        ORDER BY c.slug, s.title
        """,
        (country_slugs,),
    )


def list_country_sources(
    connection: Connection[Any],
    country_slug: str,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
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
        WHERE c.slug = %s
        ORDER BY s.title
        LIMIT %s OFFSET %s
        """,
        (country_slug, limit, offset),
    )


def count_country_sources(connection: Connection[Any], country_slug: str) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS total
        FROM sources s
        JOIN countries c ON c.id = s.country_id
        WHERE c.slug = %s
        """,
        (country_slug,),
    )
    return int(row["total"]) if row else 0


def list_legal_signals(
    connection: Connection[Any],
    locale: str,
    country_slug: str | None,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    requested_locale = validate_locale(locale)
    title_column = localized_column(requested_locale, "ls.title_en", "ls.title_ru")
    summary_column = localized_column(
        requested_locale, "ls.summary_en", "ls.summary_ru"
    )
    country_filter = "AND c.slug = %s" if country_slug else ""
    params: tuple[Any, ...] = (
        (country_slug, limit, offset) if country_slug else (limit, offset)
    )
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
            CASE
                WHEN {title_column} IS NOT NULL AND {summary_column} IS NOT NULL THEN 'exact'
                WHEN ls.title_en IS NOT NULL OR ls.summary_en IS NOT NULL OR ls.title IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END AS translation_status
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE 1 = 1 {country_filter}
        ORDER BY ls.published_date DESC NULLS LAST, ls.title
        LIMIT %s OFFSET %s
        """,
        params,
    )


def count_legal_signals(
    connection: Connection[Any], country_slug: str | None = None
) -> int:
    if country_slug:
        row = fetch_one(
            connection,
            """
            SELECT COUNT(*) AS total
            FROM legal_signals ls
            JOIN countries c ON c.id = ls.country_id
            WHERE c.slug = %s
            """,
            (country_slug,),
        )
    else:
        row = fetch_one(connection, "SELECT COUNT(*) AS total FROM legal_signals")
    return int(row["total"]) if row else 0


def get_legal_signal(
    connection: Connection[Any], signal_id: str, locale: str
) -> dict[str, Any] | None:
    requested_locale = validate_locale(locale)
    title_column = localized_column(requested_locale, "title_en", "title_ru")
    summary_column = localized_column(requested_locale, "summary_en", "summary_ru")
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
            CASE
                WHEN {title_column} IS NOT NULL AND {summary_column} IS NOT NULL THEN 'exact'
                WHEN title_en IS NOT NULL OR summary_en IS NOT NULL OR title IS NOT NULL THEN 'fallback'
                ELSE 'missing'
            END AS translation_status
        FROM legal_signals
        WHERE id::text = %s
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
        WHERE legal_signal_id::text = %s
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
            published_at,
            accessed_at,
            created_at,
            updated_at
        FROM sources
        WHERE id::text = %s
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
        WHERE source_id::text = %s
        ORDER BY retrieved_at DESC NULLS LAST, title
        LIMIT %s OFFSET %s
        """,
        (source_id, limit, offset),
    )


def count_evidence_for_source(connection: Connection[Any], source_id: str) -> int:
    row = fetch_one(
        connection,
        "SELECT COUNT(*) AS total FROM evidence_items WHERE source_id::text = %s",
        (source_id,),
    )
    return int(row["total"]) if row else 0


def list_user_stories(
    connection: Connection[Any], limit: int, offset: int
) -> list[dict[str, Any]]:
    return fetch_all(
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
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )


def count_user_stories(connection: Connection[Any]) -> int:
    row = fetch_one(connection, "SELECT COUNT(*) AS total FROM user_stories")
    return int(row["total"]) if row else 0


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
        WHERE id::text = %s
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
