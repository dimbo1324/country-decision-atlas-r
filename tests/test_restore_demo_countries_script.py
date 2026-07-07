"""scripts/dev_tools/restore_demo_countries.py: generic idempotent upsert builder."""

from scripts.dev_tools import restore_demo_countries as restore_script
from scripts.dev_tools._demo_countries_fixture_spec import TableSpec
from typing import Any


class _FakeCursor:
    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self._rows = rows or []

    def fetchall(self) -> list[dict[str, Any]]:
        return self._rows


class _FakeConnection:
    def __init__(self, column_type_rows: list[dict[str, Any]]) -> None:
        self.column_type_rows = column_type_rows
        self.executed: list[tuple[str, Any]] = []

    def execute(self, query: str, params: Any = ()) -> _FakeCursor:
        self.executed.append((query, params))
        if "information_schema.columns" in query:
            return _FakeCursor(self.column_type_rows)
        return _FakeCursor()


def _spec() -> TableSpec:
    return TableSpec(
        "countries",
        "SELECT * FROM countries WHERE slug = ANY(%(slugs)s)",
        ("id",),
    )


def _column_type_rows() -> list[dict[str, Any]]:
    return [
        {"column_name": "id", "udt_name": "uuid"},
        {"column_name": "slug", "udt_name": "text"},
        {"column_name": "is_demo", "udt_name": "bool"},
    ]


def test_param_value_serializes_lists_and_dicts_for_jsonb() -> None:
    assert restore_script._param_value(["a", "b"]) == '["a", "b"]'
    assert restore_script._param_value({"k": 1}) == '{"k": 1}'
    assert restore_script._param_value("plain") == "plain"
    assert restore_script._param_value(None) is None


def test_upsert_table_dry_run_reports_count_without_executing() -> None:
    conn = _FakeConnection(_column_type_rows())
    rows = [{"id": "c1", "slug": "wakanda", "is_demo": False}]

    count = restore_script._upsert_table(conn, _spec(), rows, dry_run=True)  # type: ignore[arg-type]

    assert count == 1
    assert all("INSERT INTO" not in q for q, _ in conn.executed)


def test_upsert_table_builds_conflict_upsert_with_explicit_casts() -> None:
    conn = _FakeConnection(_column_type_rows())
    rows = [{"id": "c1", "slug": "wakanda", "is_demo": False}]

    count = restore_script._upsert_table(conn, _spec(), rows, dry_run=False)  # type: ignore[arg-type]

    assert count == 1
    insert_calls = [q for q, _ in conn.executed if "INSERT INTO countries" in q]
    assert len(insert_calls) == 1
    sql = insert_calls[0]
    assert "ON CONFLICT (id) DO UPDATE SET" in sql
    assert "slug = %s::text" in sql
    assert "is_demo = %s::bool" in sql
    assert "%s::uuid" in sql


def test_upsert_table_empty_rows_is_a_noop() -> None:
    conn = _FakeConnection(_column_type_rows())
    count = restore_script._upsert_table(conn, _spec(), [], dry_run=False)  # type: ignore[arg-type]
    assert count == 0
    assert conn.executed == []


def test_join_table_without_extra_columns_does_nothing_on_conflict() -> None:
    conn = _FakeConnection(
        [
            {"column_name": "route_id", "udt_name": "uuid"},
            {"column_name": "source_id", "udt_name": "uuid"},
        ]
    )
    spec = TableSpec(
        "route_sources",
        "SELECT * FROM route_sources",
        ("route_id", "source_id"),
    )
    rows = [{"route_id": "r1", "source_id": "s1"}]

    restore_script._upsert_table(conn, spec, rows, dry_run=False)  # type: ignore[arg-type]

    insert_calls = [q for q, _ in conn.executed if "INSERT INTO" in q]
    assert "DO NOTHING" in insert_calls[0]
