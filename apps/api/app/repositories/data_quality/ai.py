from app.core.database import fetch_all
from psycopg import Connection
from typing import Any


AI_FEATURE_KEYS = (
    "ai_augmentation",
    "ai_grounded_qa",
    "ai_explain_number",
    "ai_nl_decision",
)


def list_missing_ai_feature_flags(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        WITH expected(feature_key) AS (
            SELECT unnest(%s::text[])
        )
        SELECT expected.feature_key
        FROM expected
        LEFT JOIN feature_flags ff ON ff.key = expected.feature_key
        WHERE ff.key IS NULL
        ORDER BY expected.feature_key
        """,
        (list(AI_FEATURE_KEYS),),
    )


def list_ai_feature_flags_without_public_access_rules(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            ff.key AS feature_key,
            ff.status,
            ff.access_tier
        FROM feature_flags ff
        LEFT JOIN feature_access_rules far
            ON far.feature_key = ff.key
            AND far.access_tier = 'public'
        WHERE ff.key = ANY(%s::text[])
          AND far.feature_key IS NULL
        ORDER BY ff.key
        """,
        (list(AI_FEATURE_KEYS),),
    )


def list_ai_logs_with_forbidden_metadata_keys(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            request_type,
            created_at,
            metadata
        FROM ai_interaction_logs
        WHERE metadata ?| ARRAY[
            'email',
            'phone',
            'name',
            'full_name',
            'telegram_user_id',
            'ip',
            'ip_address',
            'user_agent',
            'token',
            'admin_token',
            'password'
        ]
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )
