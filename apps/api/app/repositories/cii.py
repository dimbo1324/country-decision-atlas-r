from app.core.database import fetch_one
from psycopg import Connection
from typing import Any


def get_country_cii(
    connection: Connection[Any],
    country_slug: str,
    version: str = "v1.0",
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            ccs.overall_score::float AS overall_score,
            ccs.confidence,
            ccs.drift::float AS drift,
            ccs.version,
            ccs.formula_version,
            ccs.aggregation_method,
            ccs.metric_scores AS metrics,
            ccs.calculated_at
        FROM country_cii_scores ccs
        JOIN countries c ON c.id = ccs.country_id
        WHERE c.slug = %s
          AND ccs.version = %s
        """,
        (country_slug, version),
    )
