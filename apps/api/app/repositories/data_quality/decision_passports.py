from app.repositories import data_quality as data_quality_repository
from psycopg import Connection
from typing import Any


def list_active_passports_missing_scenario_slug(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, scenario_slug
        FROM decision_passports
        WHERE status = 'active'
          AND (scenario_slug IS NULL OR BTRIM(scenario_slug) = '')
        ORDER BY generated_at DESC
        """,
    )


def list_active_passports_with_empty_candidates(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, candidate_country_slugs
        FROM decision_passports
        WHERE status = 'active'
          AND jsonb_array_length(candidate_country_slugs) = 0
        ORDER BY generated_at DESC
        """,
    )


def list_active_passports_with_empty_result_snapshot(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id
        FROM decision_passports
        WHERE status = 'active'
          AND decision_result_snapshot = '{}'::jsonb
        ORDER BY generated_at DESC
        """,
    )


def list_active_passports_with_selected_country_not_in_candidates(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, selected_country_slug, candidate_country_slugs
        FROM decision_passports
        WHERE status = 'active'
          AND selected_country_slug IS NOT NULL
          AND NOT (candidate_country_slugs @> to_jsonb(selected_country_slug::text))
        ORDER BY generated_at DESC
        """,
    )


def list_passports_with_inconsistent_expiry_status(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, status, expires_at
        FROM decision_passports
        WHERE status = 'active'
          AND expires_at IS NOT NULL
          AND expires_at < NOW()
        ORDER BY generated_at DESC
        """,
    )


def list_active_passports_without_sources(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id
        FROM decision_passports
        WHERE status = 'active'
          AND jsonb_array_length(source_ids) = 0
        ORDER BY generated_at DESC
        """,
    )


def list_old_active_passports_without_expires_at(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, generated_at
        FROM decision_passports
        WHERE status = 'active'
          AND expires_at IS NULL
          AND generated_at < NOW() - INTERVAL '30 days'
        ORDER BY generated_at DESC
        """,
    )
