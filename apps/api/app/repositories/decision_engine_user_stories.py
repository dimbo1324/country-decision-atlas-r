import json
from app.core.database import execute_one, fetch_all, fetch_one
from app.repositories.sorting import resolve_sort_clause
from app.schemas.decision_engine import UserStoryCreate
from psycopg import Connection
from typing import Any


USER_STORY_SORT_COLUMNS = {
    "created_at": "us.created_at",
    "year": "us.year",
    "satisfaction_score": "us.satisfaction_score",
}


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
    sort_column, order_sql = resolve_sort_clause(
        sort, order, USER_STORY_SORT_COLUMNS, "created_at"
    )
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


def get_user_story(
    connection: Connection[Any], story_id: str
) -> dict[str, Any] | None:
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
        WHERE id = %s::uuid AND status = 'published'
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


def active_country_exists(
    connection: Connection[Any], country_slug: str
) -> bool:
    return (
        fetch_one(
            connection,
            "SELECT id FROM countries WHERE slug = %s AND is_active = TRUE",
            (country_slug,),
        )
        is not None
    )


def active_scenario_exists(
    connection: Connection[Any], scenario_slug: str
) -> bool:
    return (
        fetch_one(
            connection,
            "SELECT id FROM scenarios WHERE slug = %s AND is_active = TRUE",
            (scenario_slug,),
        )
        is not None
    )
