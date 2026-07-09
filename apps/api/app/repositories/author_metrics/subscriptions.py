from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


SUBSCRIPTION_SELECT = """
    asub.id::text AS id,
    asub.user_id::text AS user_id,
    asub.metric_id::text AS metric_id,
    amd.slug AS metric_slug,
    amd.name_en AS metric_name_en,
    amd.name_ru AS metric_name_ru,
    asub.author_user_id::text AS author_user_id,
    au.display_name AS author_display_name,
    asub.created_at
"""

SUBSCRIPTION_JOINS = """
FROM author_subscriptions asub
LEFT JOIN author_metric_definitions amd ON amd.id = asub.metric_id
LEFT JOIN users au ON au.id = asub.author_user_id
"""


def create_subscription(
    connection: Connection[Any],
    *,
    user_id: str,
    metric_id: str | None,
    author_user_id: str | None,
) -> dict[str, Any]:
    row = execute_one(
        connection,
        """
        INSERT INTO author_subscriptions (user_id, metric_id, author_user_id)
        VALUES (%s::uuid, %s::uuid, %s::uuid)
        RETURNING id::text AS id
        """,
        (user_id, metric_id, author_user_id),
    )
    subscription = get_subscription_by_id(connection, str(row["id"]))
    if subscription is None:
        raise RuntimeError(
            "Expected author subscription to exist after insert."
        )
    return subscription


def get_subscription_by_id(
    connection: Connection[Any], subscription_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {SUBSCRIPTION_SELECT}
        {SUBSCRIPTION_JOINS}
        WHERE asub.id = %s::uuid
        """,
        (subscription_id,),
    )


def get_subscription_for_target(
    connection: Connection[Any],
    *,
    user_id: str,
    metric_id: str | None,
    author_user_id: str | None,
) -> dict[str, Any] | None:
    if metric_id is not None:
        return fetch_one(
            connection,
            f"""
            SELECT
                {SUBSCRIPTION_SELECT}
            {SUBSCRIPTION_JOINS}
            WHERE asub.user_id = %s::uuid AND asub.metric_id = %s::uuid
            """,
            (user_id, metric_id),
        )
    return fetch_one(
        connection,
        f"""
        SELECT
            {SUBSCRIPTION_SELECT}
        {SUBSCRIPTION_JOINS}
        WHERE asub.user_id = %s::uuid AND asub.author_user_id = %s::uuid
        """,
        (user_id, author_user_id),
    )


def delete_subscription(
    connection: Connection[Any], subscription_id: str
) -> None:
    connection.execute(
        "DELETE FROM author_subscriptions WHERE id = %s::uuid",
        (subscription_id,),
    )


def list_subscriptions_for_user(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {SUBSCRIPTION_SELECT}
        {SUBSCRIPTION_JOINS}
        WHERE asub.user_id = %s::uuid
        ORDER BY asub.created_at DESC
        """,
        (user_id,),
    )


def count_subscribers_for_author(
    connection: Connection[Any], author_user_id: str
) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(DISTINCT asub.user_id) AS total
        FROM author_subscriptions asub
        LEFT JOIN author_metric_definitions amd ON amd.id = asub.metric_id
        WHERE asub.author_user_id = %s::uuid
           OR amd.author_user_id = %s::uuid
        """,
        (author_user_id, author_user_id),
    )
    return int(row["total"]) if row else 0


def list_feed_values_for_user(
    connection: Connection[Any], user_id: str, limit: int
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            amd.id::text AS metric_id,
            amd.slug AS metric_slug,
            amd.name_en AS metric_name_en,
            amd.name_ru AS metric_name_ru,
            amd.author_user_id::text AS author_user_id,
            u.display_name AS author_display_name,
            amv.country_id::text AS country_id,
            c.slug AS country_slug,
            COALESCE(c.name, c.slug) AS country_name,
            amv.value,
            amv.updated_at AS value_updated_at
        FROM author_subscriptions asub
        JOIN author_metric_definitions amd
            ON amd.id = asub.metric_id
            OR amd.author_user_id = asub.author_user_id
        JOIN author_metric_values amv ON amv.metric_id = amd.id
        JOIN countries c ON c.id = amv.country_id
        JOIN users u ON u.id = amd.author_user_id
        WHERE asub.user_id = %s::uuid
          AND amd.status = 'published'
          AND amd.visibility = 'public'
        ORDER BY amv.updated_at DESC
        LIMIT %s
        """,
        (user_id, limit),
    )
