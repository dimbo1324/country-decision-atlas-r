from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from psycopg.types.json import Jsonb
from typing import Any


GLOBAL_SCENARIO_SLUG = "__global__"


def normalize_scenario_slug(scenario_slug: str | None) -> str:
    if scenario_slug is None or scenario_slug.strip() == "":
        return GLOBAL_SCENARIO_SLUG
    return scenario_slug


def list_active_countries(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id,
            slug,
            name,
            iso2,
            iso3
        FROM countries
        WHERE is_active = TRUE
        ORDER BY slug
        """,
    )


def get_country_by_slug(
    connection: Connection[Any], country_slug: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            id,
            slug,
            name,
            iso2,
            iso3
        FROM countries
        WHERE slug = %s
          AND is_active = TRUE
        """,
        (country_slug,),
    )


def list_active_mvp_scenarios(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id,
            slug,
            name
        FROM scenarios
        WHERE is_active = TRUE
          AND slug = ANY(%s)
        ORDER BY array_position(%s, slug)
        """,
        (_mvp_scenario_slugs(), _mvp_scenario_slugs()),
    )


def list_legal_velocity_events(
    connection: Connection[Any],
    country_id: str,
    window_days: int,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            lse.id AS event_id,
            lse.event_date,
            lse.impact_direction,
            lse.impact_level,
            ls.signal_type,
            lse.affected_groups,
            lse.source_id,
            lse.evidence_item_id
        FROM legal_signal_events lse
        JOIN legal_signals ls ON ls.id = lse.legal_signal_id
        WHERE lse.country_id::text = %s
          AND ls.status = 'published'
          AND lse.event_date >= CURRENT_DATE - (%s::int * INTERVAL '1 day')
          AND lse.event_date <= CURRENT_DATE
        ORDER BY lse.event_date DESC, lse.id
        """,
        (country_id, window_days),
    )


def list_scenario_risk_inputs(
    connection: Connection[Any],
    country_id: str,
    scenario_slug: str,
    window_days: int,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            ls.id AS signal_id,
            lse.id AS event_id,
            COALESCE(lse.event_date, ls.published_date, ls.effective_date) AS event_date,
            ls.signal_type,
            COALESCE(lse.impact_direction, ls.impact_direction) AS impact_direction,
            COALESCE(lse.impact_level, ls.impact_level) AS impact_level,
            COALESCE(lse.affected_groups, ls.affected_groups, '[]'::jsonb) AS affected_groups,
            COALESCE(lse.source_id, ls.source_id) AS source_id,
            COALESCE(lse.evidence_item_id, ei.id) AS evidence_item_id,
            COALESCE(s.confidence, s.reliability_level) AS source_confidence,
            COALESCE(ei.confidence, ei.confidence_level) AS evidence_confidence,
            COALESCE(ls.confidence, ls.confidence_level) AS signal_confidence,
            %s AS requested_scenario_slug
        FROM legal_signals ls
        LEFT JOIN legal_signal_events lse
            ON lse.legal_signal_id = ls.id
            AND lse.event_date >= CURRENT_DATE - (%s::int * INTERVAL '1 day')
            AND lse.event_date <= CURRENT_DATE
        LEFT JOIN sources s ON s.id = COALESCE(lse.source_id, ls.source_id)
        LEFT JOIN LATERAL (
            SELECT evidence.id, evidence.confidence, evidence.confidence_level
            FROM evidence_items evidence
            WHERE evidence.status = 'published'
              AND (
                  evidence.id = lse.evidence_item_id
                  OR evidence.legal_signal_id = ls.id
              )
            ORDER BY evidence.published_at DESC NULLS LAST, evidence.created_at DESC
            LIMIT 1
        ) ei ON TRUE
        WHERE ls.country_id::text = %s
          AND ls.status = 'published'
          AND COALESCE(lse.event_date, ls.published_date, ls.effective_date, ls.created_at::date)
              >= CURRENT_DATE - (%s::int * INTERVAL '1 day')
          AND COALESCE(lse.event_date, ls.published_date, ls.effective_date, ls.created_at::date)
              <= CURRENT_DATE
        ORDER BY COALESCE(lse.event_date, ls.published_date, ls.effective_date) DESC NULLS LAST,
            ls.id
        """,
        (scenario_slug, window_days, country_id, window_days),
    )


def list_contradiction_inputs(
    connection: Connection[Any],
    country_id: str,
    window_days: int,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            ls.id AS signal_id,
            lse.id AS event_id,
            COALESCE(lse.event_date, ls.published_date, ls.effective_date) AS event_date,
            ls.signal_type,
            COALESCE(lse.affected_groups, ls.affected_groups, '[]'::jsonb) AS affected_groups,
            COALESCE(lse.impact_direction, ls.impact_direction) AS impact_direction,
            COALESCE(lse.impact_level, ls.impact_level) AS impact_level,
            s.source_type,
            COALESCE(lse.source_id, ls.source_id) AS source_id,
            COALESCE(lse.evidence_item_id, ei.id) AS evidence_item_id,
            COALESCE(ei.confidence, ei.confidence_level, ls.confidence, ls.confidence_level) AS confidence
        FROM legal_signals ls
        LEFT JOIN legal_signal_events lse
            ON lse.legal_signal_id = ls.id
            AND lse.event_date >= CURRENT_DATE - (%s::int * INTERVAL '1 day')
            AND lse.event_date <= CURRENT_DATE
        LEFT JOIN sources s ON s.id = COALESCE(lse.source_id, ls.source_id)
        LEFT JOIN LATERAL (
            SELECT evidence.id, evidence.confidence, evidence.confidence_level
            FROM evidence_items evidence
            WHERE evidence.status = 'published'
              AND (
                  evidence.id = lse.evidence_item_id
                  OR evidence.legal_signal_id = ls.id
              )
            ORDER BY evidence.published_at DESC NULLS LAST, evidence.created_at DESC
            LIMIT 1
        ) ei ON TRUE
        WHERE ls.country_id::text = %s
          AND ls.status = 'published'
          AND COALESCE(lse.event_date, ls.published_date, ls.effective_date, ls.created_at::date)
              >= CURRENT_DATE - (%s::int * INTERVAL '1 day')
          AND COALESCE(lse.event_date, ls.published_date, ls.effective_date, ls.created_at::date)
              <= CURRENT_DATE
        ORDER BY COALESCE(lse.event_date, ls.published_date, ls.effective_date) DESC NULLS LAST,
            ls.id
        """,
        (window_days, country_id, window_days),
    )


def upsert_country_platform_metric(
    connection: Connection[Any],
    country_id: str,
    metric_key: str,
    scenario_slug: str | None,
    value: Any,
    label: str,
    confidence: str,
    freshness_status: str,
    window_days: int,
    methodology_version: str,
    input_summary: dict[str, Any],
    source_count: int,
    evidence_count: int,
    signal_count: int,
    event_count: int,
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO country_platform_metrics (
            country_id,
            metric_key,
            scenario_slug,
            value,
            label,
            confidence,
            freshness_status,
            window_days,
            methodology_version,
            input_summary,
            source_count,
            evidence_count,
            signal_count,
            event_count
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (
            country_id,
            metric_key,
            scenario_slug,
            methodology_version
        )
        DO UPDATE SET
            value = EXCLUDED.value,
            label = EXCLUDED.label,
            confidence = EXCLUDED.confidence,
            freshness_status = EXCLUDED.freshness_status,
            window_days = EXCLUDED.window_days,
            input_summary = EXCLUDED.input_summary,
            source_count = EXCLUDED.source_count,
            evidence_count = EXCLUDED.evidence_count,
            signal_count = EXCLUDED.signal_count,
            event_count = EXCLUDED.event_count,
            computed_at = NOW(),
            updated_at = NOW()
        RETURNING
            id,
            country_id,
            metric_key,
            scenario_slug,
            value,
            label,
            confidence,
            freshness_status,
            window_days,
            methodology_version,
            input_summary,
            source_count,
            evidence_count,
            signal_count,
            event_count,
            computed_at,
            expires_at,
            created_at,
            updated_at
        """,
        (
            country_id,
            metric_key,
            normalize_scenario_slug(scenario_slug),
            value,
            label,
            confidence,
            freshness_status,
            window_days,
            methodology_version,
            Jsonb(input_summary),
            source_count,
            evidence_count,
            signal_count,
            event_count,
        ),
    )


def list_country_platform_metrics(
    connection: Connection[Any],
    country_slug: str,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            cpm.id,
            cpm.country_id,
            cpm.metric_key,
            cpm.scenario_slug,
            cpm.value,
            cpm.label,
            cpm.confidence,
            cpm.freshness_status,
            cpm.window_days,
            cpm.methodology_version,
            cpm.input_summary,
            cpm.source_count,
            cpm.evidence_count,
            cpm.signal_count,
            cpm.event_count,
            cpm.computed_at,
            cpm.expires_at,
            cpm.created_at,
            cpm.updated_at
        FROM country_platform_metrics cpm
        JOIN countries c ON c.id = cpm.country_id
        WHERE c.slug = %s
        ORDER BY cpm.metric_key, cpm.scenario_slug
        """,
        (country_slug,),
    )


def get_country_platform_metric(
    connection: Connection[Any],
    country_slug: str,
    metric_key: str,
    scenario_slug: str | None,
    methodology_version: str = "v1.0",
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            cpm.id,
            cpm.country_id,
            cpm.metric_key,
            cpm.scenario_slug,
            cpm.value,
            cpm.label,
            cpm.confidence,
            cpm.freshness_status,
            cpm.window_days,
            cpm.methodology_version,
            cpm.input_summary,
            cpm.source_count,
            cpm.evidence_count,
            cpm.signal_count,
            cpm.event_count,
            cpm.computed_at,
            cpm.expires_at,
            cpm.created_at,
            cpm.updated_at
        FROM country_platform_metrics cpm
        JOIN countries c ON c.id = cpm.country_id
        WHERE c.slug = %s
          AND cpm.metric_key = %s
          AND cpm.scenario_slug = %s
          AND cpm.methodology_version = %s
        """,
        (
            country_slug,
            metric_key,
            normalize_scenario_slug(scenario_slug),
            methodology_version,
        ),
    )


def list_platform_metrics_for_countries(
    connection: Connection[Any],
    country_slugs: list[str],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            cpm.id,
            cpm.country_id,
            cpm.metric_key,
            cpm.scenario_slug,
            cpm.value,
            cpm.label,
            cpm.confidence,
            cpm.freshness_status,
            cpm.window_days,
            cpm.methodology_version,
            cpm.input_summary,
            cpm.source_count,
            cpm.evidence_count,
            cpm.signal_count,
            cpm.event_count,
            cpm.computed_at,
            cpm.expires_at,
            cpm.created_at,
            cpm.updated_at
        FROM country_platform_metrics cpm
        JOIN countries c ON c.id = cpm.country_id
        WHERE c.slug = ANY(%s)
        ORDER BY c.slug, cpm.metric_key, cpm.scenario_slug
        """,
        (country_slugs,),
    )


def _mvp_scenario_slugs() -> list[str]:
    return [
        "relocation_residence",
        "permanent_residence_citizenship",
        "low_budget_living",
        "business_self_employment",
        "safety_political_risk",
    ]
