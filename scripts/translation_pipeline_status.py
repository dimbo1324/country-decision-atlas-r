from __future__ import annotations

import os
from pathlib import Path
import sys


_api_path = str(Path(__file__).resolve().parents[1] / "apps" / "api")
if _api_path not in sys.path:
    sys.path.insert(0, _api_path)

import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402


def _fetch(
    conn: psycopg.Connection[dict[str, object]],
    sql: str,
    params: tuple[object, ...] = (),
) -> list[dict[str, object]]:
    return conn.execute(sql, params).fetchall()


def _scalar(
    conn: psycopg.Connection[dict[str, object]],
    sql: str,
    params: tuple[object, ...] = (),
) -> int:
    row = conn.execute(sql, params).fetchone()
    if row is None:
        return 0
    val = row["n"]
    return int(val) if isinstance(val, (int, float, str)) else 0


def main() -> None:
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://localhost:5433/country_atlas",
    )

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        tu_total = _scalar(
            conn, "SELECT COUNT(*) AS n FROM translation_units WHERE is_active = TRUE"
        )
        tu_with_original = _scalar(
            conn,
            "SELECT COUNT(DISTINCT tu.id) AS n FROM translation_units tu "
            "JOIN translation_variants tv ON tv.translation_unit_id = tu.id AND tv.is_original = TRUE "
            "WHERE tu.is_active = TRUE",
        )

        tv_rows = _fetch(
            conn,
            "SELECT status, COUNT(*) AS n FROM translation_variants GROUP BY status ORDER BY status",
        )

        missing_en = _scalar(
            conn,
            """
            SELECT COUNT(*) AS n
            FROM translation_units tu
            JOIN translation_variants tv_orig ON tv_orig.translation_unit_id = tu.id AND tv_orig.is_original = TRUE
            LEFT JOIN translation_variants tv_en ON tv_en.translation_unit_id = tu.id AND tv_en.locale_code = 'en'
            WHERE tu.is_active = TRUE AND tv_en.id IS NULL
            """,
        )

        stale_en = _scalar(
            conn,
            """
            SELECT COUNT(*) AS n
            FROM translation_units tu
            JOIN translation_variants tv_orig ON tv_orig.translation_unit_id = tu.id AND tv_orig.is_original = TRUE
            JOIN translation_variants tv_en ON tv_en.translation_unit_id = tu.id AND tv_en.locale_code = 'en' AND tv_en.is_original = FALSE
            WHERE tu.is_active = TRUE AND tv_en.source_hash <> tu.source_hash
            """,
        )

        job_rows = _fetch(
            conn,
            "SELECT status, COUNT(*) AS n FROM translation_jobs GROUP BY status ORDER BY status",
        )

    print("=== Translation Pipeline Status ===")
    print()
    print(f"Translation units (active):  {tu_total}")
    print(f"  with original variant:     {tu_with_original}")
    print(f"  missing EN variant:        {missing_en}")
    print(f"  stale EN variant:          {stale_en}")
    print()
    print("Translation variants by status:")
    if tv_rows:
        for row in tv_rows:
            print(f"  {row['status']:25s} {row['n']}")
    else:
        print("  (none)")
    print()
    print("Translation jobs by status:")
    if job_rows:
        for row in job_rows:
            print(f"  {row['status']:25s} {row['n']}")
    else:
        print("  (none)")
    print()

    if missing_en > 0:
        print(
            f"ACTION NEEDED: {missing_en} unit(s) missing EN translation — run create-missing"
        )
    if stale_en > 0:
        print(
            f"ACTION NEEDED: {stale_en} unit(s) have stale EN translation — run create-stale"
        )
    if missing_en == 0 and stale_en == 0:
        print("OK: no missing or stale EN translations")


if __name__ == "__main__":
    main()
