"""Schema assertions for the decision-passports migration, including idempotency and token hashing."""

import pytest
from app.repositories import (
    decision_engine as decision_repository,
    decision_passports as passport_repository,
)
from app.schemas.decision_engine import DecisionRunRequest
from app.services import decision_engine, decision_passports as service
from datetime import UTC, datetime, timedelta
from fastapi import HTTPException
from pathlib import Path
from tests.test_decision_run import install_repository_fakes, payload
from tests.test_openapi_contract import load_contract
from typing import Any, cast
from unittest.mock import MagicMock


MIGRATION = Path("database/migrations/039_decision_passport.sql")
CONNECTION = cast(Any, MagicMock())


def _sql() -> str:
    return MIGRATION.read_text(encoding="utf-8")


class FakePassportStore:
    def __init__(self) -> None:
        self.rows: dict[str, dict[str, Any]] = {}
        self._next_id = 1

    def create(self, **kwargs: Any) -> dict[str, Any]:
        row: dict[str, Any] = {
            "id": f"passport-{self._next_id}",
            "generated_at": datetime.now(UTC),
            "created_at": datetime.now(UTC),
            "status": "active",
            **kwargs,
        }
        self._next_id += 1
        self.rows[str(kwargs["public_token_hash"])] = row
        return row

    def get(self, token_hash: str) -> dict[str, Any] | None:
        return self.rows.get(token_hash)


def install_passport_store(
    monkeypatch: pytest.MonkeyPatch,
) -> FakePassportStore:
    store = FakePassportStore()
    monkeypatch.setattr(
        passport_repository,
        "create_decision_passport",
        lambda _conn, **kwargs: store.create(**kwargs),
    )
    monkeypatch.setattr(
        passport_repository,
        "get_decision_passport_by_token_hash",
        lambda _conn, token_hash: store.get(token_hash),
    )
    return store


def test_migration_creates_decision_passports_table() -> None:
    assert "CREATE TABLE IF NOT EXISTS decision_passports" in _sql()


def test_migration_is_idempotent() -> None:
    sql = _sql()
    assert sql.count("CREATE TABLE IF NOT EXISTS decision_passports") == 1


def test_migration_has_token_hash_not_raw_token() -> None:
    sql = _sql()
    assert "public_token_hash" in sql
    assert "public_token TEXT" not in sql


def test_migration_does_not_touch_scoring_tables() -> None:
    sql = _sql()
    for forbidden in (
        "country_cii_scores",
        "country_scores",
        "country_score_breakdowns",
        "scenario_metric_weights",
        "country_trust_scores",
        "country_drift_snapshots",
    ):
        assert forbidden not in sql


def test_create_passport_success(monkeypatch: pytest.MonkeyPatch) -> None:
    install_repository_fakes(monkeypatch)
    install_passport_store(monkeypatch)

    response = service.create_decision_passport(
        CONNECTION, payload(), "en", None
    )

    assert response.token
    assert response.path == f"/decision/passports/{response.token}"
    assert response.passport_id


def test_create_passport_runs_decision_server_side(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    install_passport_store(monkeypatch)
    calls: list[DecisionRunRequest] = []
    original = decision_engine.run_decision

    def spy(connection: Any, request: DecisionRunRequest) -> Any:
        calls.append(request)
        return original(connection, request)

    monkeypatch.setattr(decision_engine, "run_decision", spy)

    service.create_decision_passport(CONNECTION, payload(), "en", None)

    assert len(calls) == 1


def test_create_passport_returns_token_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    store = install_passport_store(monkeypatch)

    response = service.create_decision_passport(
        CONNECTION, payload(), "en", None
    )

    stored_row = next(iter(store.rows.values()))
    assert "token" not in stored_row
    assert stored_row["public_token_hash"] != response.token


def test_db_stores_hash_not_raw_token(monkeypatch: pytest.MonkeyPatch) -> None:
    install_repository_fakes(monkeypatch)
    store = install_passport_store(monkeypatch)

    response = service.create_decision_passport(
        CONNECTION, payload(), "en", None
    )

    stored_row = next(iter(store.rows.values()))
    assert stored_row["public_token_prefix"] == response.token[:8]
    assert len(stored_row["public_token_hash"]) == 64


def test_get_passport_by_token(monkeypatch: pytest.MonkeyPatch) -> None:
    install_repository_fakes(monkeypatch)
    install_passport_store(monkeypatch)

    created = service.create_decision_passport(
        CONNECTION, payload(), "en", None
    )
    result = service.get_decision_passport_by_token(CONNECTION, created.token)

    assert result.id == created.passport_id
    assert result.status == "active"


def test_get_passport_does_not_rerun_decision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    install_passport_store(monkeypatch)
    created = service.create_decision_passport(
        CONNECTION, payload(), "en", None
    )

    def fail_if_called(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("decision engine should not run again on GET")

    monkeypatch.setattr(decision_engine, "run_decision", fail_if_called)

    result = service.get_decision_passport_by_token(CONNECTION, created.token)

    assert result.decision_result.results


def test_unknown_token_returns_404(monkeypatch: pytest.MonkeyPatch) -> None:
    install_passport_store(monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        service.get_decision_passport_by_token(CONNECTION, "unknown-token")

    assert exc_info.value.status_code == 404
    assert (
        cast(dict[str, Any], exc_info.value.detail)["error"]["code"]
        == "decision_passport_not_found"
    )


def test_expired_token_returns_410(monkeypatch: pytest.MonkeyPatch) -> None:
    install_repository_fakes(monkeypatch)
    install_passport_store(monkeypatch)
    created = service.create_decision_passport(CONNECTION, payload(), "en", 1)

    monkeypatch.setattr(
        passport_repository,
        "get_decision_passport_by_token_hash",
        lambda *_: {
            "id": created.passport_id,
            "status": "active",
            "expires_at": datetime.now(UTC) - timedelta(days=1),
            "locale": "en",
            "scenario_slug": "relocation_residence",
            "persona_slug": None,
            "origin_country_slug": None,
            "candidate_country_slugs": [],
            "selected_country_slug": None,
            "decision_result_snapshot": {},
            "methodology_snapshot": {},
            "source_ids": [],
            "route_ids": [],
            "disclaimer": "test",
            "generated_at": datetime.now(UTC),
            "created_at": datetime.now(UTC),
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        service.get_decision_passport_by_token(CONNECTION, created.token)

    assert exc_info.value.status_code == 410
    assert (
        cast(dict[str, Any], exc_info.value.detail)["error"]["code"]
        == "decision_passport_expired"
    )


def test_revoked_token_returns_410(monkeypatch: pytest.MonkeyPatch) -> None:
    install_passport_store(monkeypatch)
    monkeypatch.setattr(
        passport_repository,
        "get_decision_passport_by_token_hash",
        lambda *_: {
            "id": "passport-revoked",
            "status": "revoked",
            "expires_at": None,
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        service.get_decision_passport_by_token(CONNECTION, "revoked-token")

    assert exc_info.value.status_code == 410
    assert (
        cast(dict[str, Any], exc_info.value.detail)["error"]["code"]
        == "decision_passport_revoked"
    )


def test_invalid_decision_request_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    install_passport_store(monkeypatch)
    monkeypatch.setattr(
        decision_repository, "get_decision_scenario", lambda *_: None
    )
    bad_request = payload("unknown_scenario")

    with pytest.raises(HTTPException) as exc_info:
        service.create_decision_passport(CONNECTION, bad_request, "en", None)

    assert exc_info.value.status_code == 404


def test_persona_and_origin_preserved_in_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    install_passport_store(monkeypatch)
    request = DecisionRunRequest(
        origin_country_slug="russia",
        candidate_country_slugs=["uruguay", "russia"],
        scenario_slug="relocation_residence",
    )

    created = service.create_decision_passport(CONNECTION, request, "en", None)
    result = service.get_decision_passport_by_token(CONNECTION, created.token)

    assert result.origin_country_slug == "russia"
    assert result.methodology_snapshot.origin_country_slug == "russia"


def test_source_ids_included(monkeypatch: pytest.MonkeyPatch) -> None:
    install_repository_fakes(monkeypatch)
    install_passport_store(monkeypatch)

    created = service.create_decision_passport(
        CONNECTION, payload(), "en", None
    )
    result = service.get_decision_passport_by_token(CONNECTION, created.token)

    assert "source-1" in result.source_ids
    assert result.source_refs
    assert result.source_refs[0].id == "source-1"


def test_selected_country_slug_is_winner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_repository_fakes(monkeypatch)
    install_passport_store(monkeypatch)

    created = service.create_decision_passport(
        CONNECTION, payload(), "en", None
    )
    result = service.get_decision_passport_by_token(CONNECTION, created.token)

    assert (
        result.selected_country_slug
        == result.decision_result.results[0].country.slug
    )
    assert result.selected_country_slug == "uruguay"


def test_openapi_contains_passport_endpoints() -> None:
    contract = load_contract()

    assert "/api/v1/decision/passports" in contract["paths"]
    assert "/api/v1/decision/passports/{token}" in contract["paths"]
    for schema_name in [
        "DecisionPassportCreateRequest",
        "DecisionPassportCreateResponse",
        "DecisionPassportResponse",
        "DecisionPassportMethodologySnapshot",
        "DecisionPassportSourceRef",
        "DecisionPassportRouteRef",
    ]:
        assert schema_name in contract["components"]["schemas"]
