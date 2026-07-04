from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from psycopg.types.json import Jsonb
from typing import Any


PROFILE_FIELDS = """
    id::text AS id,
    user_id::text AS user_id,
    name,
    scenario_slug,
    weights,
    is_default,
    created_at,
    updated_at
"""


def list_profiles_for_user(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {PROFILE_FIELDS}
        FROM user_weight_profiles
        WHERE user_id::text = %s
        ORDER BY is_default DESC, updated_at DESC, name ASC
        """,
        (user_id,),
    )


def get_profile_for_user(
    connection: Connection[Any], profile_id: str, user_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {PROFILE_FIELDS}
        FROM user_weight_profiles
        WHERE id::text = %s
          AND user_id::text = %s
        """,
        (profile_id, user_id),
    )


def get_profile_by_name_for_user(
    connection: Connection[Any], user_id: str, name: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {PROFILE_FIELDS}
        FROM user_weight_profiles
        WHERE user_id::text = %s
          AND name = %s
        """,
        (user_id, name),
    )


def scenario_exists(connection: Connection[Any], scenario_slug: str) -> bool:
    row = fetch_one(
        connection,
        """
        SELECT slug
        FROM scenarios
        WHERE slug = %s
          AND is_active = TRUE
        """,
        (scenario_slug,),
    )
    return row is not None


def clear_default_profiles(
    connection: Connection[Any], user_id: str, scenario_slug: str | None
) -> None:
    fetch_all(
        connection,
        """
        UPDATE user_weight_profiles
        SET is_default = FALSE, updated_at = NOW()
        WHERE user_id::text = %s
          AND scenario_slug IS NOT DISTINCT FROM %s
          AND is_default IS TRUE
        RETURNING id
        """,
        (user_id, scenario_slug),
    )


def create_profile(
    connection: Connection[Any],
    *,
    user_id: str,
    name: str,
    scenario_slug: str | None,
    weights: dict[str, float],
    is_default: bool,
) -> dict[str, Any]:
    return execute_one(
        connection,
        f"""
        INSERT INTO user_weight_profiles (
            user_id,
            name,
            scenario_slug,
            weights,
            is_default
        ) VALUES (%s, %s, %s, %s, %s)
        RETURNING
            {PROFILE_FIELDS}
        """,
        (user_id, name, scenario_slug, Jsonb(weights), is_default),
    )


def update_profile(
    connection: Connection[Any],
    *,
    profile_id: str,
    user_id: str,
    name: str,
    scenario_slug: str | None,
    weights: dict[str, float],
    is_default: bool,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        UPDATE user_weight_profiles
        SET
            name = %s,
            scenario_slug = %s,
            weights = %s,
            is_default = %s,
            updated_at = NOW()
        WHERE id::text = %s
          AND user_id::text = %s
        RETURNING
            {PROFILE_FIELDS}
        """,
        (
            name,
            scenario_slug,
            Jsonb(weights),
            is_default,
            profile_id,
            user_id,
        ),
    )


def delete_profile(
    connection: Connection[Any], profile_id: str, user_id: str
) -> bool:
    rows = fetch_all(
        connection,
        """
        DELETE FROM user_weight_profiles
        WHERE id::text = %s
          AND user_id::text = %s
        RETURNING id
        """,
        (profile_id, user_id),
    )
    return bool(rows)
