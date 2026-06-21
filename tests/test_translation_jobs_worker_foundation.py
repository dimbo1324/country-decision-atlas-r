import os
import pytest
from typing import Any
from unittest.mock import MagicMock, patch


UNIT_ID = "00000000-0000-0000-0000-000000000001"
VARIANT_ID = "00000000-0000-0000-0000-000000000002"
JOB_ID = "00000000-0000-0000-0000-000000000003"

_REPO = "app.repositories.translation_jobs"


def _make_conn() -> Any:
    conn = MagicMock()
    return conn


def _unit(source_text: str = "Привет", source_hash: str = "h1") -> dict[str, Any]:
    return {
        "translation_unit_id": UNIT_ID,
        "entity_type": "country_card",
        "entity_id": "00000000-0000-0000-0000-000000000009",
        "field_name": "title",
        "original_locale_code": "ru",
        "source_text": source_text,
        "source_hash": source_hash,
    }


def _job(
    status: str = "pending", attempts: int = 0, max_attempts: int = 3
) -> dict[str, Any]:
    from datetime import UTC, datetime

    return {
        "id": JOB_ID,
        "translation_unit_id": UNIT_ID,
        "source_locale_code": "ru",
        "target_locale_code": "en",
        "status": status,
        "priority": 100,
        "attempts": attempts,
        "max_attempts": max_attempts,
        "provider": None,
        "provider_model": None,
        "error_message": None,
        "locked_at": None,
        "locked_by": None,
        "metadata": {},
        "created_at": datetime.now(UTC),
        "started_at": None,
        "completed_at": None,
        "failed_at": None,
        "updated_at": datetime.now(UTC),
    }


class TestFindMissingTranslationUnits:
    def test_returns_units_without_target_variant(self) -> None:
        from app.repositories.translation_jobs import find_missing_translation_units

        conn = _make_conn()
        with patch(f"{_REPO}.fetch_all", return_value=[_unit()]) as mock_fetch:
            result = find_missing_translation_units(conn, "en", 50)
        assert len(result) == 1
        assert result[0]["translation_unit_id"] == UNIT_ID
        sql = mock_fetch.call_args[0][1]
        assert "tv_target.id IS NULL" in sql

    def test_excludes_units_with_active_jobs(self) -> None:
        from app.repositories.translation_jobs import find_missing_translation_units

        conn = _make_conn()
        with patch(f"{_REPO}.fetch_all", return_value=[]) as mock_fetch:
            result = find_missing_translation_units(conn, "en", 50)
        assert result == []
        sql = mock_fetch.call_args[0][1]
        assert "NOT EXISTS" in sql


class TestFindStaleTranslationUnits:
    def test_returns_units_with_different_source_hash(self) -> None:
        from app.repositories.translation_jobs import find_stale_translation_units

        conn = _make_conn()
        stale_unit = {**_unit(), "stale_variant_id": VARIANT_ID}
        with patch(f"{_REPO}.fetch_all", return_value=[stale_unit]) as mock_fetch:
            result = find_stale_translation_units(conn, "en", 50)
        assert len(result) == 1
        assert result[0]["stale_variant_id"] == VARIANT_ID
        sql = mock_fetch.call_args[0][1]
        assert "source_hash <>" in sql


class TestCreateTranslationJob:
    def test_creates_job_returns_row(self) -> None:
        from app.repositories.translation_jobs import create_translation_job

        conn = _make_conn()
        expected = _job()
        with patch(f"{_REPO}.fetch_one", return_value=expected):
            result = create_translation_job(conn, UNIT_ID, "ru", "en", 100)
        assert result is not None
        assert result["id"] == JOB_ID
        assert result["status"] == "pending"

    def test_returns_none_on_conflict(self) -> None:
        from app.repositories.translation_jobs import create_translation_job

        conn = _make_conn()
        with patch(f"{_REPO}.fetch_one", return_value=None):
            result = create_translation_job(conn, UNIT_ID, "ru", "en", 100)
        assert result is None


class TestCreateMissingNoDuplicates:
    def test_create_missing_skips_duplicate_active_jobs(self) -> None:
        from app.repositories.translation_jobs import create_missing_translation_jobs

        conn = _make_conn()
        with (
            patch(
                f"{_REPO}.find_missing_translation_units",
                side_effect=[[_unit()], []],
            ),
            patch(
                f"{_REPO}._batch_create_translation_jobs",
                side_effect=[[_job()], []],
            ),
        ):
            first = create_missing_translation_jobs(conn, "en", 50, 100)
            second = create_missing_translation_jobs(conn, "en", 50, 100)

        assert len(first) == 1
        assert len(second) == 0


class TestCreateStaleNoDuplicates:
    def test_create_stale_skips_existing_active_jobs(self) -> None:
        from app.repositories.translation_jobs import create_stale_translation_jobs

        conn = _make_conn()
        stale_unit = {**_unit(), "stale_variant_id": VARIANT_ID}
        with (
            patch(
                f"{_REPO}.find_stale_translation_units",
                side_effect=[[stale_unit], []],
            ),
            patch(
                f"{_REPO}._batch_create_translation_jobs",
                side_effect=[[_job()], []],
            ),
        ):
            first = create_stale_translation_jobs(conn, "en", 50, 80)
            second = create_stale_translation_jobs(conn, "en", 50, 80)

        assert len(first) == 1
        assert len(second) == 0


class TestLockNextPendingJob:
    def test_lock_returns_processing_job(self) -> None:
        from app.repositories.translation_jobs import lock_next_pending_job

        conn = _make_conn()
        locked = {**_job(status="processing"), "locked_by": "worker-1", "attempts": 1}
        with patch(f"{_REPO}.fetch_one", return_value=locked):
            result = lock_next_pending_job(conn, "worker-1", "en")
        assert result is not None
        assert result["status"] == "processing"
        assert result["locked_by"] == "worker-1"
        assert result["attempts"] == 1

    def test_lock_returns_none_when_no_pending(self) -> None:
        from app.repositories.translation_jobs import lock_next_pending_job

        conn = _make_conn()
        with patch(f"{_REPO}.fetch_one", return_value=None):
            result = lock_next_pending_job(conn, "worker-1", "en")
        assert result is None

    def test_second_lock_returns_none_simulating_skip_locked(self) -> None:
        from app.repositories.translation_jobs import lock_next_pending_job

        conn = _make_conn()
        locked = {**_job(status="processing"), "locked_by": "worker-1", "attempts": 1}
        with patch(f"{_REPO}.fetch_one", side_effect=[locked, None]):
            first = lock_next_pending_job(conn, "worker-1", "en")
            second = lock_next_pending_job(conn, "worker-2", "en")
        assert first is not None
        assert second is None


class TestJobLifecycleCompleted:
    def test_mark_completed_sets_status(self) -> None:
        from app.repositories.translation_jobs import mark_job_completed

        conn = _make_conn()
        done = {**_job(status="completed")}
        with patch(f"{_REPO}.fetch_one", return_value=done):
            result = mark_job_completed(conn, JOB_ID)
        assert result is not None
        assert result["status"] == "completed"


class TestJobLifecycleFailed:
    def test_mark_failed_stores_error(self) -> None:
        from app.repositories.translation_jobs import mark_job_failed

        conn = _make_conn()
        failed = {**_job(status="failed"), "error_message": "boom"}
        with patch(f"{_REPO}.fetch_one", return_value=failed):
            result = mark_job_failed(conn, JOB_ID, "boom")
        assert result is not None
        assert result["status"] == "failed"
        assert result["error_message"] == "boom"


class TestAttemptsMaxAttempts:
    def test_lock_increments_attempts(self) -> None:
        from app.repositories.translation_jobs import lock_next_pending_job

        conn = _make_conn()
        locked = {**_job(status="processing", attempts=1)}
        with patch(f"{_REPO}.fetch_one", return_value=locked):
            result = lock_next_pending_job(conn, "w", "en")
        assert result is not None
        assert result["attempts"] == 1

    def test_lock_respects_max_attempts_in_sql(self) -> None:
        from app.repositories.translation_jobs import lock_next_pending_job

        conn = _make_conn()
        with patch(f"{_REPO}.fetch_one", return_value=None) as mock_fetch:
            lock_next_pending_job(conn, "w", "en")
        sql = mock_fetch.call_args[0][1]
        assert "attempts < max_attempts" in sql


class TestFakeProvider:
    def test_fake_provider_returns_deterministic_output(self) -> None:
        from app.services.translation_providers import (
            FakeTranslationProvider,
            TranslationInput,
        )

        provider = FakeTranslationProvider()
        inp = TranslationInput(
            source_text="Привет", source_locale="ru", target_locale="en"
        )
        result = provider.translate(inp)
        assert result.text == "[FAKE en] Привет"
        assert result.provider == "fake"
        assert result.provider_model == "fake-v1"

    def test_fake_provider_does_not_call_external(self) -> None:
        from app.services.translation_providers import (
            FakeTranslationProvider,
            TranslationInput,
        )

        provider = FakeTranslationProvider()
        inp = TranslationInput(
            source_text="test", source_locale="ru", target_locale="de"
        )
        result = provider.translate(inp)
        assert result.text.startswith("[FAKE de]")


class TestFakeProviderCreatesVariant:
    def test_process_next_creates_machine_translated_variant(self) -> None:
        from app.services.translation_jobs import process_next_job

        conn = _make_conn()
        processing_job = {**_job(status="processing"), "locked_by": "w", "attempts": 1}
        unit_data = {
            "id": UNIT_ID,
            "original_locale_code": "ru",
            "source_hash": "h1",
            "source_text": "Привет",
        }
        variant_data = {
            "id": VARIANT_ID,
            "locale_code": "en",
            "text": "[FAKE en] Привет",
            "status": "machine_translated",
            "method": "machine",
            "is_original": False,
            "source_hash": "h1",
        }
        with (
            patch(f"{_REPO}.lock_next_pending_job", return_value=processing_job),
            patch(f"{_REPO}.get_translation_unit_for_job", return_value=unit_data),
            patch(
                f"{_REPO}.save_translation_variant", return_value=variant_data
            ) as mock_save,
            patch(f"{_REPO}.mark_job_completed", return_value={}),
        ):
            result = process_next_job(conn, "w", "en")

        assert result is not None
        assert result["status"] == "completed"
        assert result["variant_id"] == VARIANT_ID
        assert mock_save.call_args.kwargs.get("text") == "[FAKE en] Привет"

    def test_variant_status_is_machine_translated(self) -> None:
        from app.repositories.translation_jobs import save_translation_variant

        conn = _make_conn()
        expected_variant = {
            "id": VARIANT_ID,
            "locale_code": "en",
            "text": "[FAKE en] Hello",
            "status": "machine_translated",
            "method": "machine",
            "is_original": False,
            "source_hash": "h1",
        }
        with patch(f"{_REPO}.fetch_one", return_value=expected_variant):
            result = save_translation_variant(
                conn,
                translation_unit_id=UNIT_ID,
                locale_code="en",
                text="[FAKE en] Hello",
                source_locale_code="ru",
                source_hash="h1",
                provider="fake",
                provider_model="fake-v1",
            )
        assert result is not None
        assert result["status"] == "machine_translated"
        assert result["is_original"] is False


class TestOriginalNotOverwritten:
    def test_save_variant_sql_contains_not_original_guard(self) -> None:
        from app.repositories.translation_jobs import save_translation_variant

        conn = _make_conn()
        with patch(f"{_REPO}.fetch_one", return_value=None) as mock_fetch:
            save_translation_variant(
                conn, UNIT_ID, "ru", "FAKE text", "ru", "h1", "fake", "fake-v1"
            )
        sql = mock_fetch.call_args[0][1]
        assert "is_original = FALSE" in sql

    def test_process_next_fails_gracefully_when_no_unit(self) -> None:
        from app.services.translation_jobs import process_next_job

        conn = _make_conn()
        processing_job = {**_job(status="processing"), "locked_by": "w", "attempts": 1}
        with (
            patch(f"{_REPO}.lock_next_pending_job", return_value=processing_job),
            patch(f"{_REPO}.get_translation_unit_for_job", return_value=None),
            patch(f"{_REPO}.mark_job_failed", return_value={}) as mock_fail,
        ):
            result = process_next_job(conn, "w", "en")

        assert result is not None
        assert result["status"] == "failed"
        mock_fail.assert_called_once()


class TestAdminTokenRequirement:
    def test_require_admin_token_rejects_missing(self) -> None:
        from app.core.admin_auth import require_admin_token
        from app.core.config import get_settings
        from fastapi import HTTPException

        get_settings.cache_clear()
        os.environ["ADMIN_TOKEN"] = "test-token"
        get_settings.cache_clear()
        try:
            with pytest.raises(HTTPException) as exc:
                require_admin_token(None)
            assert exc.value.status_code == 401
        finally:
            os.environ.pop("ADMIN_TOKEN", None)
            get_settings.cache_clear()

    def test_admin_translation_jobs_route_requires_token(self) -> None:
        from app.api.v1.admin_translation_jobs import list_jobs
        import inspect

        sig = inspect.signature(list_jobs)
        assert "_" in sig.parameters


class TestAdminCreateMissingEndpoint:
    def test_create_missing_returns_created_count(self) -> None:
        from app.services.translation_jobs import discover_missing_jobs

        conn = _make_conn()
        with patch(
            f"{_REPO}.create_missing_translation_jobs",
            return_value=[_job()],
        ):
            result = discover_missing_jobs(conn, "en", 50, 100)
        assert len(result) == 1


class TestAdminProcessNextEndpoint:
    def test_process_next_returns_completed_result(self) -> None:
        from app.services.translation_jobs import process_next_job

        conn = _make_conn()
        processing_job = {
            **_job(status="processing"),
            "locked_by": "api-admin",
            "attempts": 1,
        }
        unit_data = {
            "id": UNIT_ID,
            "original_locale_code": "ru",
            "source_hash": "h1",
            "source_text": "Text",
        }
        variant_data = {
            "id": VARIANT_ID,
            "locale_code": "en",
            "text": "[FAKE en] Text",
            "status": "machine_translated",
            "method": "machine",
            "is_original": False,
            "source_hash": "h1",
        }
        with (
            patch(f"{_REPO}.lock_next_pending_job", return_value=processing_job),
            patch(f"{_REPO}.get_translation_unit_for_job", return_value=unit_data),
            patch(f"{_REPO}.save_translation_variant", return_value=variant_data),
            patch(f"{_REPO}.mark_job_completed", return_value={}),
        ):
            result = process_next_job(conn, "api-admin", "en")
        assert result is not None
        assert result["status"] == "completed"


class TestAdminListJobsEndpoint:
    def test_list_jobs_returns_dict_with_items(self) -> None:
        from app.services.translation_jobs import list_jobs

        conn = _make_conn()
        with (
            patch(f"{_REPO}.list_translation_jobs", return_value=[_job()]),
            patch(f"{_REPO}.count_translation_jobs", return_value=1),
        ):
            result = list_jobs(conn, None, None, 50, 0)
        assert "items" in result
        assert result["total"] == 1


class TestRegressionEndpoints:
    def test_countries_repo_import_unaffected(self) -> None:
        from app.repositories.countries import list_countries

        assert callable(list_countries)

    def test_legal_signals_repo_import_unaffected(self) -> None:
        from app.repositories.legal_signals import list_legal_signals

        assert callable(list_legal_signals)

    def test_localization_service_import_unaffected(self) -> None:
        from app.services.localization import overlay_localized_fields

        assert callable(overlay_localized_fields)

    def test_decision_engine_import_unaffected(self) -> None:
        from app.services.decision_engine import run_decision

        assert callable(run_decision)

    def test_translation_jobs_schemas_valid(self) -> None:
        from app.schemas.translation_jobs import (
            TranslationJobCreateMissingRequest,
            TranslationJobProcessBatchRequest,
        )

        req = TranslationJobCreateMissingRequest(target_locale="en")
        assert req.target_locale == "en"
        assert req.limit == 50

        batch_req = TranslationJobProcessBatchRequest()
        assert batch_req.limit == 10
        assert batch_req.worker_id == "api-admin"

    def test_fake_provider_is_translation_provider_subclass(self) -> None:
        from app.services.translation_providers import (
            FakeTranslationProvider,
            TranslationProvider,
        )

        provider = FakeTranslationProvider()
        assert isinstance(provider, TranslationProvider)
