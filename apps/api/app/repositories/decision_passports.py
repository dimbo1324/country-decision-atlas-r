from app.core.database import execute_one, fetch_all, fetch_one
from datetime import datetime
from psycopg import Connection
from psycopg.types.json import Jsonb
from typing import Any


PASSPORT_FIELDS = """
    id::text AS id,
    public_token_prefix,
    locale,
    scenario_slug,
    persona_slug,
    origin_country_slug,
    candidate_country_slugs,
    selected_country_slug,
    decision_request,
    decision_result_snapshot,
    methodology_snapshot,
    source_ids,
    route_ids,
    disclaimer,
    status,
    generated_at,
    expires_at,
    created_at
"""


def create_decision_passport(
    connection: Connection[Any],
    *,
    public_token_hash: str,
    public_token_prefix: str,
    locale: str,
    scenario_slug: str,
    persona_slug: str | None,
    origin_country_slug: str | None,
    candidate_country_slugs: list[str],
    selected_country_slug: str | None,
    decision_request: dict[str, Any],
    decision_result_snapshot: dict[str, Any],
    methodology_snapshot: dict[str, Any],
    source_ids: list[str],
    route_ids: list[str],
    disclaimer: str,
    expires_at: datetime | None,
) -> dict[str, Any]:
    return execute_one(
        connection,
        f"""
        INSERT INTO decision_passports (
            public_token_hash,
            public_token_prefix,
            locale,
            scenario_slug,
            persona_slug,
            origin_country_slug,
            candidate_country_slugs,
            selected_country_slug,
            decision_request,
            decision_result_snapshot,
            methodology_snapshot,
            source_ids,
            route_ids,
            disclaimer,
            expires_at
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        RETURNING
            {PASSPORT_FIELDS}
        """,
        (
            public_token_hash,
            public_token_prefix,
            locale,
            scenario_slug,
            persona_slug,
            origin_country_slug,
            Jsonb(candidate_country_slugs),
            selected_country_slug,
            Jsonb(decision_request),
            Jsonb(decision_result_snapshot),
            Jsonb(methodology_snapshot),
            Jsonb(source_ids),
            Jsonb(route_ids),
            disclaimer,
            expires_at,
        ),
    )


def get_decision_passport_by_token_hash(
    connection: Connection[Any], token_hash: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {PASSPORT_FIELDS}
        FROM decision_passports
        WHERE public_token_hash = %s
        """,
        (token_hash,),
    )


def mark_expired_passports(connection: Connection[Any]) -> int:
    rows = fetch_all(
        connection,
        """
        UPDATE decision_passports
        SET status = 'expired'
        WHERE status = 'active'
          AND expires_at IS NOT NULL
          AND expires_at < NOW()
        RETURNING id
        """,
    )
    return len(rows)


def revoke_decision_passport(
    connection: Connection[Any], passport_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        UPDATE decision_passports
        SET status = 'revoked'
        WHERE id::text = %s
        RETURNING
            {PASSPORT_FIELDS}
        """,
        (passport_id,),
    )


def count_active_decision_passports(connection: Connection[Any]) -> int:
    row = fetch_one(
        connection,
        "SELECT COUNT(*) AS total FROM decision_passports WHERE status = 'active'",
    )
    return int(row["total"]) if row else 0


def list_passport_quality_findings(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            scenario_slug,
            selected_country_slug,
            candidate_country_slugs,
            decision_result_snapshot,
            source_ids,
            expires_at,
            generated_at
        FROM decision_passports
        WHERE status = 'active'
        ORDER BY generated_at DESC
        """,
    )
