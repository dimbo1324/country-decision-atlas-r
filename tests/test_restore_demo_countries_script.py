"""scripts/dev_tools/restore_demo_countries.py: generic idempotent upsert builder."""

import re
from scripts.dev_tools import restore_demo_countries as restore_script
from scripts.dev_tools._demo_countries_fixture_spec import TableSpec
from typing import Any


class _FakeCursor:
    def __init__(
        self, rows: list[dict[str, Any]] | None = None, rowcount: int = 0
    ) -> None:
        self._rows = rows or []
        self.rowcount = rowcount

    def fetchall(self) -> list[dict[str, Any]]:
        return self._rows


class _FakeConnection:
    def __init__(
        self,
        column_type_rows: list[dict[str, Any]],
        lookup_rows_by_table: dict[str, list[dict[str, Any]]] | None = None,
        update_rowcount: int = 0,
    ) -> None:
        self.column_type_rows = column_type_rows
        self.lookup_rows_by_table = lookup_rows_by_table or {}
        self.update_rowcount = update_rowcount
        self.executed: list[tuple[str, Any]] = []

    def execute(self, query: str, params: Any = ()) -> _FakeCursor:
        self.executed.append((query, params))
        if "information_schema.columns" in query:
            return _FakeCursor(self.column_type_rows)
        if query.strip().startswith("UPDATE countries"):
            return _FakeCursor(rowcount=self.update_rowcount)
        match = re.search(r"FROM (\w+) WHERE", query)
        if match:
            return _FakeCursor(
                self.lookup_rows_by_table.get(match.group(1), [])
            )
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


def test_restore_demo_countries_visible_flips_is_demo_and_is_active_via_update() -> (
    None
):
    conn = _FakeConnection(_column_type_rows(), update_rowcount=3)

    result = restore_script.restore_demo_countries(
        conn,  # type: ignore[arg-type]
        dry_run=False,
        visible=True,
    )

    update_calls = [q for q, _ in conn.executed if "UPDATE countries" in q]
    assert len(update_calls) == 1
    assert "is_demo = FALSE" in update_calls[0]
    assert "is_active = TRUE" in update_calls[0]
    assert result == {"countries": 3}


def test_restore_demo_countries_visible_dry_run_does_not_touch_db() -> None:
    conn = _FakeConnection(_column_type_rows())

    result = restore_script.restore_demo_countries(
        conn,  # type: ignore[arg-type]
        dry_run=True,
        visible=True,
    )

    assert conn.executed == []
    assert result == {"countries": 3}


def test_restore_demo_countries_default_uses_fixture_upsert_not_update(
    monkeypatch: Any,
) -> None:
    captured_rows: dict[str, list[dict[str, Any]]] = {}

    def fake_load_rows(spec: TableSpec) -> list[dict[str, Any]]:
        if spec.name == "countries":
            return [{"id": "c1", "slug": "russia", "is_demo": True}]
        return []

    def fake_upsert_table(
        _connection: Any,
        spec: TableSpec,
        rows: list[dict[str, Any]],
        **_kwargs: Any,
    ) -> int:
        captured_rows[spec.name] = rows
        return len(rows)

    monkeypatch.setattr(restore_script, "_load_rows", fake_load_rows)
    monkeypatch.setattr(restore_script, "_load_json_fixture", lambda _name: [])
    monkeypatch.setattr(restore_script, "_upsert_table", fake_upsert_table)
    conn = _FakeConnection(_column_type_rows())

    restore_script.restore_demo_countries(
        conn,  # type: ignore[arg-type]
        dry_run=False,
    )

    assert captured_rows["countries"] == [
        {"id": "c1", "slug": "russia", "is_demo": True}
    ]
    assert all("UPDATE countries" not in q for q, _ in conn.executed)


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


def test_lookup_id_remap_maps_stale_fixture_id_to_existing_db_id() -> None:
    conn = _FakeConnection(
        _column_type_rows(),
        lookup_rows_by_table={
            "countries": [{"slug": "russia", "id": "existing-id"}]
        },
    )
    fixture_rows = [{"id": "stale-fixture-id", "slug": "russia"}]

    remap = restore_script._lookup_id_remap(
        conn,  # type: ignore[arg-type]
        "countries",
        "slug",
        fixture_rows,
    )

    assert remap == {"stale-fixture-id": "existing-id"}


def test_lookup_id_remap_empty_when_fixture_id_matches_existing() -> None:
    conn = _FakeConnection(
        _column_type_rows(),
        lookup_rows_by_table={"locales": [{"code": "ru", "id": "same-id"}]},
    )
    fixture_rows = [{"id": "same-id", "code": "ru"}]

    remap = restore_script._lookup_id_remap(
        conn,  # type: ignore[arg-type]
        "locales",
        "code",
        fixture_rows,
    )

    assert remap == {}


def test_lookup_id_remap_empty_when_no_existing_row() -> None:
    conn = _FakeConnection(_column_type_rows())
    fixture_rows = [{"id": "fixture-id", "slug": "residence"}]

    remap = restore_script._lookup_id_remap(
        conn,  # type: ignore[arg-type]
        "scenarios",
        "slug",
        fixture_rows,
    )

    assert remap == {}


def test_lookup_id_remap_empty_when_no_fixture_rows() -> None:
    conn = _FakeConnection(_column_type_rows())

    remap = restore_script._lookup_id_remap(conn, "countries", "slug", [])  # type: ignore[arg-type]

    assert remap == {}
    assert conn.executed == []


def test_build_id_remap_merges_countries_and_external_lookups(
    monkeypatch: Any,
) -> None:
    conn = _FakeConnection(
        _column_type_rows(),
        lookup_rows_by_table={
            "countries": [{"slug": "russia", "id": "new-country-id"}],
            "locales": [{"code": "ru", "id": "new-locale-id"}],
            "scenarios": [{"slug": "residence", "id": "new-scenario-id"}],
            "cii_metric_definitions": [
                {"slug": "safety", "id": "new-metric-id"}
            ],
        },
    )

    def fake_load_json_fixture(name: str) -> list[dict[str, Any]]:
        sidecars = {
            "_lookup_locales": [{"id": "old-locale-id", "code": "ru"}],
            "_lookup_scenarios": [
                {"id": "old-scenario-id", "slug": "residence"}
            ],
            "_lookup_cii_metric_definitions": [
                {"id": "old-metric-id", "slug": "safety"}
            ],
        }
        return sidecars.get(name, [])

    monkeypatch.setattr(
        restore_script, "_load_json_fixture", fake_load_json_fixture
    )

    remap = restore_script._build_id_remap(
        conn,  # type: ignore[arg-type]
        [{"id": "old-country-id", "slug": "russia"}],
    )

    assert remap == {
        "old-country-id": "new-country-id",
        "old-locale-id": "new-locale-id",
        "old-scenario-id": "new-scenario-id",
        "old-metric-id": "new-metric-id",
    }


def test_remap_row_replaces_matching_string_values() -> None:
    remap = {"old-id": "new-id"}
    row = {"id": "row-1", "country_id": "old-id", "slug": "russia"}

    result = restore_script._remap_row(row, remap)

    assert result == {"id": "row-1", "country_id": "new-id", "slug": "russia"}


def test_remap_row_returns_row_unchanged_when_remap_empty() -> None:
    row = {"id": "row-1", "country_id": "old-id"}

    result = restore_script._remap_row(row, {})

    assert result == row


def test_restore_demo_countries_remaps_dependent_table_country_id_reference(
    monkeypatch: Any,
) -> None:
    captured_rows: dict[str, list[dict[str, Any]]] = {}

    def fake_load_rows(spec: TableSpec) -> list[dict[str, Any]]:
        if spec.name == "countries":
            return [{"id": "stale-id", "slug": "russia", "is_demo": True}]
        if spec.name == "sources":
            return [{"id": "source-1", "country_id": "stale-id"}]
        return []

    def fake_upsert_table(
        _connection: Any,
        spec: TableSpec,
        rows: list[dict[str, Any]],
        **_kwargs: Any,
    ) -> int:
        captured_rows[spec.name] = rows
        return len(rows)

    monkeypatch.setattr(restore_script, "_load_rows", fake_load_rows)
    monkeypatch.setattr(restore_script, "_load_json_fixture", lambda _name: [])
    monkeypatch.setattr(restore_script, "_upsert_table", fake_upsert_table)
    conn = _FakeConnection(
        _column_type_rows(),
        lookup_rows_by_table={
            "countries": [{"slug": "russia", "id": "existing-id"}]
        },
    )

    restore_script.restore_demo_countries(
        conn,  # type: ignore[arg-type]
        dry_run=False,
    )

    assert captured_rows["countries"] == [
        {"id": "existing-id", "slug": "russia", "is_demo": True}
    ]
    assert captured_rows["sources"] == [
        {"id": "source-1", "country_id": "existing-id"}
    ]
