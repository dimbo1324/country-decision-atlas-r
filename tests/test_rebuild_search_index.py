from app.repositories import search_index as search_index_repository
from psycopg import Connection
import pytest
import scripts.rebuild_search_index as rebuild_script
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def _country_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "entity_id": "country-1",
        "country_slug": "argentina",
        "locale": "en",
        "title": "Argentina",
        "summary": "Executive summary",
        "body": "Body text",
        "path_slug": "argentina",
        "updated_at": None,
    }
    row.update(overrides)
    return row


def _route_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "entity_id": "route-1",
        "country_slug": "argentina",
        "title_en": "Temporary residence",
        "title_ru": "Временное проживание",
        "summary_en": "Summary EN",
        "summary_ru": "Summary RU",
        "path_id": "route-1",
        "updated_at": None,
    }
    row.update(overrides)
    return row


def _source_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "entity_id": "source-1",
        "country_slug": "argentina",
        "title": "Immigration law",
        "summary": "Publisher",
        "updated_at": None,
    }
    row.update(overrides)
    return row


def install_no_op_upsert(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    def fake_upsert(_connection: Any, **kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs)
        return kwargs

    monkeypatch.setattr(search_index_repository, "upsert_search_document", fake_upsert)
    return calls


def install_all_jobs_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    for entity_type in rebuild_script.ENTITY_JOBS:
        monkeypatch.setitem(
            rebuild_script.ENTITY_JOBS[entity_type], "fetch", lambda *_: []
        )
    monkeypatch.setattr(
        search_index_repository, "list_indexed_entity_ids", lambda *_a: []
    )
    monkeypatch.setattr(
        search_index_repository, "delete_search_documents_by_ids", lambda *_a: 0
    )


def test_rebuild_all_processes_every_entity_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_no_op_upsert(monkeypatch)
    install_all_jobs_empty(monkeypatch)

    result = rebuild_script.rebuild(CONNECTION, None, None, dry_run=False)

    assert result["ok"] is True
    assert result["summary"]["entity_types_processed"] == len(
        rebuild_script.ENTITY_JOBS
    )
    assert result["errors"] == []


def test_rebuild_indexes_dual_locale_route(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = install_no_op_upsert(monkeypatch)
    install_all_jobs_empty(monkeypatch)
    monkeypatch.setitem(
        rebuild_script.ENTITY_JOBS["route"], "fetch", lambda *_: [_route_row()]
    )

    result = rebuild_script.rebuild(CONNECTION, ["route"], None, dry_run=False)

    assert result["ok"] is True
    locales = {call["locale"] for call in calls}
    assert locales == {"en", "ru"}
    assert result["summary"]["documents_upserted"] == 2


def test_rebuild_indexes_locale_partitioned_country(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = install_no_op_upsert(monkeypatch)
    install_all_jobs_empty(monkeypatch)
    monkeypatch.setitem(
        rebuild_script.ENTITY_JOBS["country"],
        "fetch",
        lambda *_: [_country_row(locale="en"), _country_row(locale="ru")],
    )

    result = rebuild_script.rebuild(CONNECTION, ["country"], None, dry_run=False)

    assert result["ok"] is True
    assert result["summary"]["documents_upserted"] == 2
    assert {call["locale"] for call in calls} == {"en", "ru"}


def test_rebuild_indexes_single_locale_both_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = install_no_op_upsert(monkeypatch)
    install_all_jobs_empty(monkeypatch)
    monkeypatch.setitem(
        rebuild_script.ENTITY_JOBS["source"], "fetch", lambda *_: [_source_row()]
    )

    result = rebuild_script.rebuild(CONNECTION, ["source"], None, dry_run=False)

    assert result["ok"] is True
    assert result["summary"]["documents_upserted"] == 2
    assert all(call["title"] == "Immigration law" for call in calls)


def test_rebuild_skips_invalid_rows_missing_title(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = install_no_op_upsert(monkeypatch)
    install_all_jobs_empty(monkeypatch)
    monkeypatch.setitem(
        rebuild_script.ENTITY_JOBS["source"],
        "fetch",
        lambda *_: [_source_row(title="")],
    )

    result = rebuild_script.rebuild(CONNECTION, ["source"], None, dry_run=False)

    assert result["summary"]["skipped_invalid"] == 2
    assert calls == []


def test_rebuild_country_filter_excludes_other_countries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = install_no_op_upsert(monkeypatch)
    install_all_jobs_empty(monkeypatch)
    monkeypatch.setitem(
        rebuild_script.ENTITY_JOBS["route"],
        "fetch",
        lambda *_: [
            _route_row(entity_id="route-ar", country_slug="argentina"),
            _route_row(entity_id="route-cl", country_slug="chile"),
        ],
    )

    result = rebuild_script.rebuild(CONNECTION, ["route"], "argentina", dry_run=False)

    assert result["ok"] is True
    assert all(call["country_slug"] == "argentina" for call in calls)
    assert result["summary"]["documents_upserted"] == 2


def test_rebuild_dry_run_does_not_upsert(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = install_no_op_upsert(monkeypatch)
    install_all_jobs_empty(monkeypatch)
    monkeypatch.setitem(
        rebuild_script.ENTITY_JOBS["route"], "fetch", lambda *_: [_route_row()]
    )

    result = rebuild_script.rebuild(CONNECTION, ["route"], None, dry_run=True)

    assert result["dry_run"] is True
    assert calls == []
    assert result["summary"]["documents_upserted"] == 2


def test_rebuild_deletes_stale_documents_not_in_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_no_op_upsert(monkeypatch)
    install_all_jobs_empty(monkeypatch)
    monkeypatch.setitem(
        rebuild_script.ENTITY_JOBS["route"], "fetch", lambda *_: [_route_row()]
    )
    monkeypatch.setattr(
        search_index_repository,
        "list_indexed_entity_ids",
        lambda *_a: [
            {"entity_id": "route-1", "locale": "en"},
            {"entity_id": "route-1", "locale": "ru"},
            {"entity_id": "stale-route", "locale": "en"},
        ],
    )
    deleted_calls: list[Any] = []

    def fake_delete(_connection: Any, _entity_type: str, stale: Any) -> int:
        deleted_calls.append(stale)
        return len(stale)

    monkeypatch.setattr(
        search_index_repository, "delete_search_documents_by_ids", fake_delete
    )

    result = rebuild_script.rebuild(CONNECTION, ["route"], None, dry_run=False)

    assert result["summary"]["documents_deleted"] == 1
    assert deleted_calls[0] == [("stale-route", "en")]


def test_rebuild_country_filter_skips_stale_deletion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_no_op_upsert(monkeypatch)
    install_all_jobs_empty(monkeypatch)
    monkeypatch.setitem(
        rebuild_script.ENTITY_JOBS["route"], "fetch", lambda *_: [_route_row()]
    )

    def fail_list_indexed(*_a: Any) -> list[dict[str, Any]]:
        raise AssertionError("should not be called when country filter is set")

    monkeypatch.setattr(
        search_index_repository, "list_indexed_entity_ids", fail_list_indexed
    )

    result = rebuild_script.rebuild(CONNECTION, ["route"], "argentina", dry_run=False)

    assert result["ok"] is True
    assert result["summary"]["documents_deleted"] == 0


def test_rebuild_unknown_entity_type_reports_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_no_op_upsert(monkeypatch)
    install_all_jobs_empty(monkeypatch)

    result = rebuild_script.rebuild(
        CONNECTION, ["not_a_real_type"], None, dry_run=False
    )

    assert result["ok"] is False
    assert any("unknown_entity_type" in error for error in result["errors"])


def test_rebuild_catches_fetch_exceptions_per_entity_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_no_op_upsert(monkeypatch)
    install_all_jobs_empty(monkeypatch)

    def failing_fetch(*_a: Any) -> list[dict[str, Any]]:
        raise RuntimeError("boom")

    monkeypatch.setitem(rebuild_script.ENTITY_JOBS["route"], "fetch", failing_fetch)

    result = rebuild_script.rebuild(
        CONNECTION, ["route", "source"], None, dry_run=False
    )

    assert result["ok"] is False
    assert any("route:" in error for error in result["errors"])
    assert result["summary"]["entity_types_processed"] == 1


def test_main_rejects_unknown_entity_type_without_touching_db(
    monkeypatch: pytest.MonkeyPatch, capsys: Any
) -> None:
    def fail_connect(*_a: Any, **_kw: Any) -> Any:
        raise AssertionError("should not connect for a validation failure")

    monkeypatch.setattr(rebuild_script, "connect", fail_connect)

    exit_code = rebuild_script.main(["--entity-type", "not_a_real_type"])

    assert exit_code == 1
    assert "unknown_entity_type" in capsys.readouterr().out


def test_content_hash_is_deterministic() -> None:
    first = rebuild_script._content_hash("route", "route-1", "en", "Title", "Summary")
    second = rebuild_script._content_hash("route", "route-1", "en", "Title", "Summary")
    different = rebuild_script._content_hash(
        "route", "route-1", "en", "Title", "Changed summary"
    )

    assert first == second
    assert first != different
