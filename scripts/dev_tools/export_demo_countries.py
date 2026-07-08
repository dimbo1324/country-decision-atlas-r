from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


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
)


def _write_fixture(name: str, rows: list[dict[str, object]]) -> None:
    target = FIXTURES_DIR / f"{name}.json"
    target.write_text(
        json.dumps(rows, indent=2, default=str, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def export_demo_countries(
    connection: psycopg.Connection[dict[str, object]],
) -> dict[str, int]:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for spec in TABLE_SPECS:
        cursor = connection.execute(
            spec.select_sql, {"slugs": list(DEMO_SLUGS)}
        )
        rows = cursor.fetchall()
        _write_fixture(spec.name, rows)
        counts[spec.name] = len(rows)
    for lookup in EXTERNAL_LOOKUPS:
        cursor = connection.execute(
            f"SELECT id, {lookup.natural_key} FROM {lookup.table}"
        )
        rows = cursor.fetchall()
        _write_fixture(f"_lookup_{lookup.table}", rows)
        counts[f"_lookup_{lookup.table}"] = len(rows)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export the conserved demo country dataset (russia, uruguay, "
            "argentina) to JSON fixtures under database/fixtures/demo_countries/."
        )
    )
    parser.parse_args()

    settings = get_settings()
    try:
        with psycopg.connect(
            settings.database_url, row_factory=psycopg.rows.dict_row
        ) as conn:
            counts = export_demo_countries(conn)
    except psycopg.OperationalError as exc:
        print(f"DB connection error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({"exported": counts}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
