"""User-story relation validation, payload limits, and rate-limiter forwarded-for handling."""

import app.main as main_module
import pytest
import yaml
from app.core.mvp_requirements import (
    MVP_CONTENT_DEPTH_TARGETS,
    MVP_READINESS_THRESHOLDS,
)
from app.main import _rate_limit_client, ready
from app.schemas.decision_engine import UserStoryCreate
from app.schemas.translation_jobs import TranslationJobProcessBatchRequest
from app.services import decision_engine, translation_jobs
from app.services.score_labels import optional_score_label, score_label
from fastapi import HTTPException
from pathlib import Path
from pydantic import ValidationError
from scripts.apply_migrations import (
    migration_checksum,
    verify_or_record_checksum,
)
from starlette.requests import Request
from tests.methodology_test_helpers import score_label_thresholds
from typing import Any, cast
from unittest.mock import MagicMock, patch


JOB_ID = "00000000-0000-0000-0000-000000000001"
UNIT_ID = "00000000-0000-0000-0000-000000000002"


def _story(**overrides: Any) -> UserStoryCreate:
    data = {
        "origin_country_slug": "russia",
        "destination_country_slug": "argentina",
        "scenario": "relocation_residence",
    }
    data.update(overrides)
    return UserStoryCreate(**data)


def _request(client: str, forwarded: str) -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/api/v1/countries",
            "raw_path": b"/api/v1/countries",
            "query_string": b"",
            "headers": [(b"x-forwarded-for", forwarded.encode())],
            "client": (client, 1234),
            "server": ("testserver", 80),
        }
    )


def _job() -> dict[str, Any]:
    return {
        "id": JOB_ID,
        "translation_unit_id": UNIT_ID,
        "source_locale_code": "ru",
        "target_locale_code": "en",
        "status": "pending",
        "attempts": 0,
    }


def _unit() -> dict[str, Any]:
    return {
        "id": UNIT_ID,
        "original_locale_code": "ru",
        "source_hash": "hash",
        "source_text": "Текст",
    }


@pytest.mark.parametrize(
    ("exists", "field", "code"),
    [
        ([False], "origin_country_slug", "user_story_country_invalid"),
        (
            [True, False],
            "destination_country_slug",
            "user_story_country_invalid",
        ),
        ([True, True, False], "scenario", "user_story_scenario_invalid"),
    ],
)
def test_user_story_relations_are_validated_before_insert(
    exists: list[bool], field: str, code: str
) -> None:
    connection = MagicMock()
    country_results = exists[:2]
    scenario_result = exists[2] if len(exists) == 3 else True
    with (
        patch(
            "app.repositories.decision_engine.active_country_exists",
            side_effect=country_results,
        ),
        patch(
            "app.repositories.decision_engine.active_scenario_exists",
            return_value=scenario_result,
        ),
        patch("app.repositories.decision_engine.create_user_story") as create,
        pytest.raises(HTTPException) as error,
    ):
        decision_engine.create_user_story(connection, _story())
    detail = cast(dict[str, Any], error.value.detail)
    assert error.value.status_code == 422
    assert detail["error"]["code"] == code
    assert detail["error"]["details"]["field"] == field
    create.assert_not_called()


def test_user_story_payload_limits() -> None:
    with pytest.raises(ValidationError):
        _story(city="x" * 121)
    with pytest.raises(ValidationError):
        _story(documents_used=["document"] * 31)
    with pytest.raises(ValidationError):
        _story(advice="x" * 4001)


def test_rate_limiter_ignores_forwarded_for_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(main_module.settings, "trusted_proxy_headers", False)
    request = _request("10.0.0.5", "203.0.113.10")
    assert _rate_limit_client(request) == "10.0.0.5"


def test_rate_limiter_uses_forwarded_for_only_when_client_is_trusted_proxy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(main_module.settings, "trusted_proxy_headers", True)
    monkeypatch.setattr(main_module.settings, "trusted_proxy_ips", "10.0.0.5")
    request = _request("10.0.0.5", "203.0.113.10")
    assert _rate_limit_client(request) == "203.0.113.10"


def test_rate_limiter_ignores_forwarded_for_from_untrusted_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(main_module.settings, "trusted_proxy_headers", True)
    monkeypatch.setattr(
        main_module.settings, "trusted_proxy_ips", "203.0.113.99"
    )
    request = _request("10.0.0.5", "203.0.113.10")
    assert _rate_limit_client(request) == "10.0.0.5"


def test_internal_routes_fail_closed_without_app_env() -> None:
    source = Path("apps/web/src/middleware.ts").read_text(encoding="utf-8")
    assert 'process.env.APP_ENV ?? "production"' in source
    assert 'process.env.APP_ENV ?? "local"' not in source


def test_translation_dry_run_does_not_claim_or_write() -> None:
    connection = MagicMock()
    with (
        patch(
            "app.repositories.translation_jobs.list_pending_jobs_for_preview",
            return_value=[_job()],
        ),
        patch(
            "app.repositories.translation_jobs.get_translation_unit_for_job",
            return_value=_unit(),
        ),
        patch(
            "app.repositories.translation_jobs.lock_next_pending_job"
        ) as lock,
        patch("app.repositories.translation_jobs.mark_job_failed") as failed,
        patch(
            "app.repositories.translation_jobs.mark_job_completed"
        ) as completed,
        patch(
            "app.repositories.translation_jobs.save_translation_variant"
        ) as save,
    ):
        first = translation_jobs.process_next_job(
            connection, "preview", "en", dry_run=True
        )
        second = translation_jobs.process_next_job(
            connection, "preview", "en", dry_run=True
        )
    assert first is not None and first["status"] == "dry_run"
    assert second is not None and second["status"] == "dry_run"
    lock.assert_not_called()
    failed.assert_not_called()
    completed.assert_not_called()
    save.assert_not_called()
    connection.commit.assert_not_called()


def test_stale_processing_recovery_is_retryable() -> None:
    from app.repositories.translation_jobs import recover_stale_processing_jobs

    connection = MagicMock()
    with patch(
        "app.repositories.translation_jobs.fetch_all", return_value=[]
    ) as fetch:
        recover_stale_processing_jobs(connection, 900, 100)
    sql = fetch.call_args.args[1]
    assert "status = 'pending'" in sql
    assert "attempts = GREATEST(attempts - 1, 0)" in sql
    assert "locked_at = NULL" in sql
    assert "FOR UPDATE SKIP LOCKED" in sql


def test_translation_batch_limits() -> None:
    assert TranslationJobProcessBatchRequest(limit=100).limit == 100
    with pytest.raises(ValidationError):
        TranslationJobProcessBatchRequest(limit=101)
    with pytest.raises(ValidationError):
        TranslationJobProcessBatchRequest(worker_id="x" * 101)


def test_migration_checksum_changes_with_content(tmp_path: Path) -> None:
    path = tmp_path / "001_test.sql"
    path.write_text("SELECT 1;", encoding="utf-8")
    first = migration_checksum(path)
    path.write_text("SELECT 2;", encoding="utf-8")
    assert migration_checksum(path) != first


def test_migration_checksum_mismatch_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "001_test.sql"
    path.write_text("SELECT 1;", encoding="utf-8")
    with pytest.raises(RuntimeError, match="Checksum mismatch"):
        verify_or_record_checksum(MagicMock(), path, "not-the-current-checksum")


def test_migration_runner_uses_advisory_lock() -> None:
    source = Path("scripts/apply_migrations.py").read_text(encoding="utf-8")
    assert "pg_advisory_lock" in source
    assert "pg_advisory_unlock" in source


@pytest.mark.parametrize(
    ("value", "label"),
    [
        (0.0, "weak"),
        (29.99, "weak"),
        (30.0, "limited"),
        (49.99, "limited"),
        (50.0, "moderate"),
        (69.99, "moderate"),
        (70.0, "strong"),
        (84.99, "strong"),
        (85.0, "excellent"),
        (100.0, "excellent"),
    ],
)
def test_score_label_boundaries(value: float, label: str) -> None:
    thresholds = score_label_thresholds()
    assert score_label(value, thresholds) == label
    assert optional_score_label(value, thresholds) == label


def test_readiness_checks_database(monkeypatch: pytest.MonkeyPatch) -> None:
    connection = MagicMock()
    pool = MagicMock()
    pool.connection.return_value.__enter__.return_value = connection
    monkeypatch.setattr(main_module, "get_pool", lambda: pool)
    response = ready()
    assert response.database == "ok"
    connection.execute.assert_called_once_with("SELECT 1")


def test_readiness_returns_controlled_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        main_module,
        "get_pool",
        MagicMock(side_effect=RuntimeError("unavailable")),
    )
    with pytest.raises(HTTPException) as error:
        ready()
    detail = cast(dict[str, Any], error.value.detail)
    assert error.value.status_code == 503
    assert detail["error"]["code"] == "readiness_database_unavailable"


def test_committed_openapi_matches_runtime_paths_and_schemas() -> None:
    committed = yaml.safe_load(
        Path("contracts/openapi.yaml").read_text(encoding="utf-8")
    )
    runtime = main_module.app.openapi()
    assert committed["paths"] == runtime["paths"]
    assert (
        committed["components"]["schemas"] == runtime["components"]["schemas"]
    )


def test_mvp_thresholds_separate_readiness_from_future_depth() -> None:
    assert MVP_READINESS_THRESHOLDS["minimum_sources"] == 10
    assert MVP_READINESS_THRESHOLDS["minimum_evidence_items"] == 15
    assert MVP_READINESS_THRESHOLDS["minimum_legal_signals"] == 5
    assert MVP_CONTENT_DEPTH_TARGETS["published_sources"] == 15
    assert MVP_CONTENT_DEPTH_TARGETS["published_evidence_items"] == 20
    assert MVP_CONTENT_DEPTH_TARGETS["published_legal_signals"] == 8


def test_argentina_decision_migration_has_all_scenarios_and_breakdowns() -> (
    None
):
    sql = Path("database/migrations/025_audit_stabilization.sql").read_text(
        encoding="utf-8"
    )
    for scenario in (
        "relocation_residence",
        "permanent_residence_citizenship",
        "low_budget_living",
        "business_self_employment",
        "safety_political_risk",
    ):
        assert scenario in sql
    for criterion in (
        "legalization_score",
        "long_term_status_score",
        "cost_of_living_score",
        "safety_score",
        "business_score",
        "legal_stability_score",
        "source_quality_score",
    ):
        assert criterion in sql
    assert "source_ids" in sql
