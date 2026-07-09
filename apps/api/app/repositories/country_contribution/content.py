from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


CARD_FIELDS = (
    "executive_summary",
    "migration_overview",
    "tax_overview",
    "cost_of_living_overview",
    "business_overview",
    "safety_overview",
    "legal_signals_summary",
    "risk_summary",
    "source_summary",
)


def get_card(
    connection: Connection[Any], *, country_id: str, locale: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT id, country_id, locale, status,
               executive_summary, migration_overview, tax_overview,
               cost_of_living_overview, business_overview, safety_overview,
               legal_signals_summary, risk_summary, source_summary
        FROM country_cards
        WHERE country_id = %s::uuid AND locale = %s
        """,
        (country_id, locale),
    )


def upsert_card(
    connection: Connection[Any],
    *,
    country_id: str,
    locale: str,
    fields: dict[str, str],
) -> dict[str, Any]:
    columns = ["country_id", "locale", *CARD_FIELDS]
    values = [country_id, locale, *(fields[key] for key in CARD_FIELDS)]
    placeholders = ", ".join(["%s"] * len(values))
    update_clause = ", ".join(f"{key} = EXCLUDED.{key}" for key in CARD_FIELDS)
    return execute_one(
        connection,
        f"""
        INSERT INTO country_cards ({", ".join(columns)})
        VALUES ({placeholders})
        ON CONFLICT (country_id, locale) DO UPDATE
        SET {update_clause}
        RETURNING id, country_id, locale, status,
                  executive_summary, migration_overview, tax_overview,
                  cost_of_living_overview, business_overview, safety_overview,
                  legal_signals_summary, risk_summary, source_summary
        """,
        values,
    )


def get_legal_signal_country_id(
    connection: Connection[Any], legal_signal_id: str
) -> str | None:
    row = fetch_one(
        connection,
        "SELECT country_id::text AS country_id FROM legal_signals WHERE id = %s::uuid",
        (legal_signal_id,),
    )
    return str(row["country_id"]) if row else None


def create_timeline_event(
    connection: Connection[Any], *, country_id: str, data: dict[str, Any]
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO legal_signal_events (
            legal_signal_id, country_id, event_date, event_type,
            impact_direction, impact_level, title, summary,
            source_id, evidence_item_id, affected_groups
        )
        VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        RETURNING id, legal_signal_id, country_id, event_date, event_type,
                  impact_direction, impact_level, title, summary,
                  source_id, evidence_item_id, affected_groups
        """,
        (
            data["legal_signal_id"],
            country_id,
            data["event_date"],
            data["event_type"],
            data["impact_direction"],
            data["impact_level"],
            data["title"],
            data["summary"],
            data["source_id"],
            data["evidence_item_id"],
            data["affected_groups"],
        ),
    )


def get_cii_metric_id_by_slug(
    connection: Connection[Any], slug: str
) -> str | None:
    row = fetch_one(
        connection,
        "SELECT id::text AS id FROM cii_metric_definitions WHERE slug = %s AND is_active = TRUE",
        (slug,),
    )
    return str(row["id"]) if row else None


def upsert_metric_value(
    connection: Connection[Any],
    *,
    country_id: str,
    metric_id: str,
    raw_value: float,
    normalized_value: float,
    data_year: int | None,
    source_name: str | None,
    source_url: str | None,
    reliability: str,
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO country_metric_values (
            country_id, metric_id, raw_value, normalized_value,
            data_year, source_name, source_url, reliability
        )
        VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (country_id, metric_id) DO UPDATE
        SET raw_value = EXCLUDED.raw_value,
            normalized_value = EXCLUDED.normalized_value,
            data_year = EXCLUDED.data_year,
            source_name = EXCLUDED.source_name,
            source_url = EXCLUDED.source_url,
            reliability = EXCLUDED.reliability
        RETURNING id, country_id, metric_id, raw_value, normalized_value,
                  data_year, source_name, source_url, reliability
        """,
        (
            country_id,
            metric_id,
            raw_value,
            normalized_value,
            data_year,
            source_name,
            source_url,
            reliability,
        ),
    )


def list_metric_values_for_country(
    connection: Connection[Any], country_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT cmv.id, cmv.country_id, cmv.metric_id, cmd.slug AS metric_slug,
               cmv.raw_value, cmv.normalized_value, cmv.data_year,
               cmv.source_name, cmv.source_url, cmv.reliability
        FROM country_metric_values cmv
        JOIN cii_metric_definitions cmd ON cmd.id = cmv.metric_id
        WHERE cmv.country_id = %s::uuid
        """,
        (country_id,),
    )


def source_exists(connection: Connection[Any], source_id: str) -> bool:
    return (
        fetch_one(
            connection,
            "SELECT 1 FROM sources WHERE id = %s::uuid",
            (source_id,),
        )
        is not None
    )


def evidence_item_exists(
    connection: Connection[Any], evidence_item_id: str
) -> bool:
    return (
        fetch_one(
            connection,
            "SELECT 1 FROM evidence_items WHERE id = %s::uuid",
            (evidence_item_id,),
        )
        is not None
    )
