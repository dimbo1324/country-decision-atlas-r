from app.core.database import fetch_one
from psycopg import Connection
from typing import Any


def get_country_base(
    connection: Connection[Any], country_slug: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT id, slug, name, iso2, is_active
        FROM countries
        WHERE slug = %s
        """,
        (country_slug,),
    )


def count_published_country_cards(
    connection: Connection[Any], country_slug: str
) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(cc.id)::int AS cnt
        FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE c.slug = %s
          AND cc.status = 'published'
        """,
        (country_slug,),
    )
    return int(row["cnt"]) if row else 0


def count_active_cii_metrics(connection: Connection[Any]) -> int:
    row = fetch_one(
        connection,
        "SELECT COUNT(id)::int AS cnt FROM cii_metric_definitions WHERE is_active = TRUE",
        (),
    )
    return int(row["cnt"]) if row else 0


def count_country_cii_metric_values(
    connection: Connection[Any], country_slug: str
) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(cmv.id)::int AS cnt
        FROM country_metric_values cmv
        JOIN countries c ON c.id = cmv.country_id
        JOIN cii_metric_definitions m ON m.id = cmv.metric_id
        WHERE c.slug = %s
          AND m.is_active = TRUE
        """,
        (country_slug,),
    )
    return int(row["cnt"]) if row else 0


def count_cii_scenario_scores(
    connection: Connection[Any],
    country_slug: str,
    scenario_slugs: tuple[str, ...],
) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(ccs.id)::int AS cnt
        FROM country_cii_scores ccs
        JOIN countries c ON c.id = ccs.country_id
        WHERE c.slug = %s
          AND ccs.scenario_slug = ANY(%s)
          AND ccs.version = 'v1.0'
        """,
        (country_slug, list(scenario_slugs)),
    )
    return int(row["cnt"]) if row else 0


def count_published_sources(connection: Connection[Any], country_slug: str) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(s.id)::int AS cnt
        FROM sources s
        JOIN countries c ON c.id = s.country_id
        WHERE c.slug = %s
          AND s.status = 'published'
        """,
        (country_slug,),
    )
    return int(row["cnt"]) if row else 0


def count_published_evidence(connection: Connection[Any], country_slug: str) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(e.id)::int AS cnt
        FROM evidence_items e
        JOIN countries c ON c.id = e.country_id
        WHERE c.slug = %s
          AND e.status = 'published'
        """,
        (country_slug,),
    )
    return int(row["cnt"]) if row else 0


def count_published_legal_signals(
    connection: Connection[Any], country_slug: str
) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(ls.id)::int AS cnt
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        WHERE c.slug = %s
          AND ls.status = 'published'
        """,
        (country_slug,),
    )
    return int(row["cnt"]) if row else 0


def count_timeline_events(connection: Connection[Any], country_slug: str) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(lse.id)::int AS cnt
        FROM legal_signal_events lse
        JOIN countries c ON c.id = lse.country_id
        WHERE c.slug = %s
        """,
        (country_slug,),
    )
    return int(row["cnt"]) if row else 0


def count_timeline_events_with_traceability(
    connection: Connection[Any], country_slug: str
) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(lse.id)::int AS cnt
        FROM legal_signal_events lse
        JOIN countries c ON c.id = lse.country_id
        WHERE c.slug = %s
          AND (lse.source_id IS NOT NULL OR lse.evidence_item_id IS NOT NULL)
        """,
        (country_slug,),
    )
    return int(row["cnt"]) if row else 0


def check_localization_metadata(connection: Connection[Any], country_slug: str) -> bool:
    row = fetch_one(
        connection,
        """
        SELECT id
        FROM countries
        WHERE slug = %s
          AND name IS NOT NULL
          AND name <> ''
          AND iso2 IS NOT NULL
          AND iso2 <> ''
        """,
        (country_slug,),
    )
    return row is not None
