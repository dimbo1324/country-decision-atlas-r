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


def _load_rows(spec: TableSpec) -> list[dict[str, Any]]:
    fixture_path = FIXTURES_DIR / f"{spec.name}.json"
    if not fixture_path.exists():
        return []
    rows: list[dict[str, Any]] = json.loads(
        fixture_path.read_text(encoding="utf-8")
    )
    return rows


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


def restore_demo_countries(
    connection: psycopg.Connection[dict[str, Any]],
    *,
    dry_run: bool,
    visible: bool = False,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for spec in TABLE_SPECS:
        rows = _load_rows(spec)
        if visible and spec.name == "countries":
            rows = [{**row, "is_demo": False} for row in rows]
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
            "Restore countries with is_demo=FALSE instead of TRUE. For "
            "CI/dev/full-gate provisioning of a fresh database, where the "
            "demo dataset needs to be publicly visible so smoke checks and "
            "E2E have content to assert against. Omit this flag for normal "
            "restores, which keep the demo set hidden per the Episode 5 "
            "decision (is_demo=TRUE)."
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
