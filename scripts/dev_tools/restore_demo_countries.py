from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "apps" / "api"))
    sys.path.insert(0, str(ROOT_DIR))

import psycopg  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from scripts.dev_tools._demo_countries_fixture_spec import (  # noqa: E402
    DEMO_SLUGS,
    EXTERNAL_LOOKUPS,
    FIXTURES_DIR,
    TABLE_SPECS,
    TableSpec,
)


def _column_types(
    connection: psycopg.Connection[dict[str, Any]], table_name: str
) -> dict[str, str]:
    cursor = connection.execute(
        """
        SELECT column_name, udt_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        """,
        (table_name,),
    )
    return {row["column_name"]: row["udt_name"] for row in cursor.fetchall()}


def _load_json_fixture(name: str) -> list[dict[str, Any]]:
    fixture_path = FIXTURES_DIR / f"{name}.json"
    if not fixture_path.exists():
        return []
    rows: list[dict[str, Any]] = json.loads(
        fixture_path.read_text(encoding="utf-8")
    )
    return rows


def _load_rows(spec: TableSpec) -> list[dict[str, Any]]:
    return _load_json_fixture(spec.name)


def _lookup_id_remap(
    connection: psycopg.Connection[dict[str, Any]],
    table: str,
    natural_key: str,
    fixture_rows: list[dict[str, Any]],
) -> dict[str, str]:
    """Map a fixture-exported id to whatever id its natural key has now.

    `countries.id`, `locales.id`, `scenarios.id`, and
    `cii_metric_definitions.id` all come from `gen_random_uuid()` with no
    fixed seed, so a fixture exported from one database instance embeds ids
    that a different fresh instance will never reproduce. `natural_key`
    (slug/code) is the stable column used to find the current row instead.
    """
    keys = [row[natural_key] for row in fixture_rows]
    if not keys:
        return {}
    cursor = connection.execute(
        f"SELECT {natural_key}, id::text AS id FROM {table} WHERE {natural_key} = ANY(%s)",
        (keys,),
    )
    existing_by_key = {row[natural_key]: row["id"] for row in cursor.fetchall()}
    remap: dict[str, str] = {}
    for row in fixture_rows:
        existing_id = existing_by_key.get(row[natural_key])
        fixture_id = str(row["id"])
        if existing_id is not None and existing_id != fixture_id:
            remap[fixture_id] = existing_id
    return remap


def _build_id_remap(
    connection: psycopg.Connection[dict[str, Any]],
    country_rows: list[dict[str, Any]],
) -> dict[str, str]:
    remap = dict(
        _lookup_id_remap(connection, "countries", "slug", country_rows)
    )
    for lookup in EXTERNAL_LOOKUPS:
        lookup_rows = _load_json_fixture(f"_lookup_{lookup.table}")
        remap.update(
            _lookup_id_remap(
                connection, lookup.table, lookup.natural_key, lookup_rows
            )
        )
    return remap


def _remap_row(row: dict[str, Any], remap: dict[str, str]) -> dict[str, Any]:
    if not remap:
        return row
    return {
        key: remap.get(value, value) if isinstance(value, str) else value
        for key, value in row.items()
    }


def _param_value(value: Any) -> Any:
    if isinstance(value, list | dict):
        return json.dumps(value)
    return value


def _upsert_table(
    connection: psycopg.Connection[dict[str, Any]],
    spec: TableSpec,
    rows: list[dict[str, Any]],
    *,
    dry_run: bool,
) -> int:
    if not rows:
        return 0
    column_types = _column_types(connection, spec.name)
    columns = list(rows[0].keys())
    update_columns = [
        col for col in columns if col not in spec.conflict_columns
    ]
    assignments = ", ".join(
        f"{col} = %s::{column_types[col]}" for col in update_columns
    )
    placeholders = ", ".join(f"%s::{column_types[col]}" for col in columns)
    conflict_clause = (
        f"DO UPDATE SET {assignments}" if update_columns else "DO NOTHING"
    )
    sql = f"""
        INSERT INTO {spec.name} ({", ".join(columns)})
        VALUES ({placeholders})
        ON CONFLICT ({", ".join(spec.conflict_columns)}) {conflict_clause}
    """
    if dry_run:
        return len(rows)
    for row in rows:
        insert_params = [_param_value(row[col]) for col in columns]
        update_params = [_param_value(row[col]) for col in update_columns]
        connection.execute(sql, insert_params + update_params)
    return len(rows)


def _ensure_demo_countries_visible(
    connection: psycopg.Connection[dict[str, Any]], *, dry_run: bool
) -> dict[str, int]:
    """Flip is_demo off for a database that already has the demo content.

    Migrations 002 onward seed russia/uruguay/argentina's full dependent
    content (profiles, cards, sources, scores, routes, ...) directly via
    same-migration subqueries against countries.slug, so on any freshly
    migrated database that content already exists and is internally
    consistent. Re-inserting it from the exported JSON fixtures would be
    redundant and, worse, collide with those already-seeded rows on their
    natural-key constraints (e.g. country_profiles.country_id UNIQUE,
    country_scores UNIQUE (country_id, scenario_id)) since those rows keep
    whatever surrogate id the fresh migration run assigned them, not the
    id captured in the fixture. Visibility only needs the flag flipped.
    """
    if dry_run:
        return {"countries": len(DEMO_SLUGS)}
    cursor = connection.execute(
        "UPDATE countries SET is_demo = FALSE, is_active = TRUE WHERE slug = ANY(%s)",
        (list(DEMO_SLUGS),),
    )
    return {"countries": cursor.rowcount}


def restore_demo_countries(
    connection: psycopg.Connection[dict[str, Any]],
    *,
    dry_run: bool,
    visible: bool = False,
) -> dict[str, int]:
    if visible:
        return _ensure_demo_countries_visible(connection, dry_run=dry_run)

    countries_spec = next(
        spec for spec in TABLE_SPECS if spec.name == "countries"
    )
    country_rows = _load_rows(countries_spec)
    remap = _build_id_remap(connection, country_rows)

    counts: dict[str, int] = {}
    for spec in TABLE_SPECS:
        rows = country_rows if spec is countries_spec else _load_rows(spec)
        rows = [_remap_row(row, remap) for row in rows]
        counts[spec.name] = _upsert_table(
            connection, spec, rows, dry_run=dry_run
        )
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Idempotently restore the conserved demo country dataset "
            "(russia, uruguay, argentina) from database/fixtures/demo_countries/."
        )
    )
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument(
        "--visible",
        action="store_true",
        default=False,
        help=(
            "For CI/dev/full-gate provisioning of a fresh database: just "
            "flip is_demo=FALSE and is_active=TRUE for russia/uruguay/"
            "argentina (their dependent content is already seeded by "
            "migrations 002+; re-inserting it from fixtures would collide "
            "with those rows' own ids). Omit this flag for the full "
            "fixture-based disaster-recovery restore, which keeps the "
            "demo set hidden per the Episode 5 decision (is_demo=TRUE)."
        ),
    )
    args = parser.parse_args()

    settings = get_settings()
    try:
        with psycopg.connect(
            settings.database_url, row_factory=psycopg.rows.dict_row
        ) as conn:
            counts = restore_demo_countries(
                conn, dry_run=args.dry_run, visible=args.visible
            )
            if not args.dry_run:
                conn.commit()
    except psycopg.OperationalError as exc:
        print(f"DB connection error: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "dry_run": args.dry_run,
                "visible": args.visible,
                "restored": counts,
            },
            indent=2,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
