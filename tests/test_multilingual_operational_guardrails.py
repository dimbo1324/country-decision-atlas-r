from __future__ import annotations

import os
from typing import Any
from unittest.mock import MagicMock, patch


_REPO = "app.repositories.translation_jobs"
UNIT_ID = "00000000-0000-0000-0000-000000000001"
JOB_ID_1 = "00000000-0000-0000-0000-000000000010"
JOB_ID_2 = "00000000-0000-0000-0000-000000000011"
VARIANT_ID = "00000000-0000-0000-0000-000000000020"


def _job(job_id: str, status: str = "processing") -> dict[str, Any]:
    from datetime import UTC, datetime

    return {
        "id": job_id,
        "translation_unit_id": UNIT_ID,
        "source_locale_code": "ru",
        "target_locale_code": "en",
        "status": status,
        "priority": 100,
        "attempts": 1,
        "max_attempts": 3,
        "provider": None,
        "provider_model": None,
        "error_message": None,
        "locked_at": None,
        "locked_by": "test-worker",
        "metadata": {},
        "created_at": datetime.now(UTC),
        "started_at": datetime.now(UTC),
        "completed_at": None,
        "failed_at": None,
        "updated_at": datetime.now(UTC),
    }


def _unit() -> dict[str, Any]:
    return {
        "id": UNIT_ID,
        "original_locale_code": "ru",
        "source_hash": "sha256-abc123",
        "source_text": "Налоговый резидент Уругвая",
    }


def _variant(text: str = "[FAKE en] Налоговый резидент Уругвая") -> dict[str, Any]:
    return {
        "id": VARIANT_ID,
        "locale_code": "en",
        "text": text,
        "status": "machine_translated",
        "method": "machine",
        "is_original": False,
        "source_hash": "sha256-abc123",
    }


class TestEndToEndPipelineSmoke:
    def test_create_missing_then_process_batch_produces_variant(self) -> None:
        from app.services.translation_jobs import discover_missing_jobs, process_batch
        from app.services.translation_providers import FakeTranslationProvider

        conn = MagicMock()
        job1 = _job(JOB_ID_1)
        job2 = _job(JOB_ID_2)
        unit = _unit()
        variant = _variant()

        with (
            patch(
                f"{_REPO}.create_missing_translation_jobs", return_value=[job1, job2]
            ),
            patch(
                f"{_REPO}.lock_next_pending_job",
                side_effect=[job1, job2, None],
            ),
            patch(f"{_REPO}.get_translation_unit_for_job", return_value=unit),
            patch(
                f"{_REPO}.save_translation_variant", return_value=variant
            ) as mock_save,
            patch(f"{_REPO}.mark_job_completed", return_value={}),
        ):
            created = discover_missing_jobs(conn, "en", 10, 100)
            result = process_batch(
                conn, "guardrail-worker", "en", 5, FakeTranslationProvider()
            )

        assert len(created) == 2
        assert result["processed"] == 2
        assert result["completed"] == 2
        assert result["failed"] == 0
        assert mock_save.call_count == 2

        saved_text = (
            mock_save.call_args_list[0].kwargs.get("text")
            or mock_save.call_args_list[0][1]["text"]
        )
        assert saved_text.startswith("[FAKE en]")

    def test_batch_result_contains_variant_ids(self) -> None:
        from app.services.translation_jobs import process_batch
        from app.services.translation_providers import FakeTranslationProvider

        conn = MagicMock()
        unit = _unit()
        variant = _variant()

        with (
            patch(f"{_REPO}.lock_next_pending_job", side_effect=[_job(JOB_ID_1), None]),
            patch(f"{_REPO}.get_translation_unit_for_job", return_value=unit),
            patch(f"{_REPO}.save_translation_variant", return_value=variant),
            patch(f"{_REPO}.mark_job_completed", return_value={}),
        ):
            result = process_batch(
                conn, "guardrail-worker", "en", 5, FakeTranslationProvider()
            )

        assert result["processed"] == 1
        assert result["results"][0]["variant_id"] == VARIANT_ID
        assert result["results"][0]["status"] == "completed"


class TestTranslationProviderDefault:
    def test_default_provider_is_fake(self) -> None:
        from app.core.config import get_settings
        from app.services.translation_providers import (
            FakeTranslationProvider,
            get_translation_provider,
        )

        get_settings.cache_clear()
        os.environ.pop("TRANSLATION_PROVIDER", None)
        get_settings.cache_clear()
        try:
            provider = get_translation_provider()
            assert isinstance(provider, FakeTranslationProvider)
        finally:
            get_settings.cache_clear()

    def test_default_mode_requires_no_api_key(self) -> None:
        from app.core.config import get_settings
        from app.services.translation_providers import get_translation_provider

        get_settings.cache_clear()
        os.environ.pop("TRANSLATION_PROVIDER", None)
        os.environ.pop("AI_TRANSLATION_API_KEY", None)
        get_settings.cache_clear()
        try:
            provider = get_translation_provider()
            assert provider is not None
        finally:
            get_settings.cache_clear()

    def test_settings_translation_provider_field_defaults_to_fake(self) -> None:
        from app.core.config import get_settings

        get_settings.cache_clear()
        os.environ.pop("TRANSLATION_PROVIDER", None)
        get_settings.cache_clear()
        try:
            settings = get_settings()
            assert settings.translation_provider.lower() == "fake"
        finally:
            get_settings.cache_clear()

    def test_ai_provider_requires_key_only_when_explicitly_set(self) -> None:
        from app.core.config import get_settings
        from app.services.translation_providers import get_translation_provider
        import pytest

        get_settings.cache_clear()
        os.environ["TRANSLATION_PROVIDER"] = "ai"
        os.environ.pop("AI_TRANSLATION_API_KEY", None)
        get_settings.cache_clear()
        try:
            with pytest.raises(RuntimeError, match="AI_TRANSLATION_API_KEY"):
                get_translation_provider()
        finally:
            os.environ.pop("TRANSLATION_PROVIDER", None)
            get_settings.cache_clear()


class TestOriginalVariantProtection:
    def test_save_translation_variant_sql_guards_original(self) -> None:
        from app.repositories.translation_jobs import save_translation_variant

        conn = MagicMock()
        with patch(f"{_REPO}.fetch_one", return_value=None) as mock_fetch:
            save_translation_variant(
                conn,
                translation_unit_id=UNIT_ID,
                locale_code="ru",
                text="attempting to overwrite original",
                source_locale_code="ru",
                source_hash="xyz",
                provider="fake",
                provider_model="fake-v1",
            )

        sql = mock_fetch.call_args[0][1]
        assert "is_original = FALSE" in sql

    def test_on_conflict_does_not_update_original(self) -> None:
        from app.repositories.translation_jobs import save_translation_variant

        conn = MagicMock()
        with patch(f"{_REPO}.fetch_one", return_value=None) as mock_fetch:
            save_translation_variant(
                conn,
                translation_unit_id=UNIT_ID,
                locale_code="en",
                text="new translation",
                source_locale_code="ru",
                source_hash="abc",
                provider="fake",
                provider_model="fake-v1",
            )

        sql = mock_fetch.call_args[0][1]
        assert "ON CONFLICT" in sql
        assert "DO UPDATE SET" in sql
        assert "WHERE translation_variants.is_original = FALSE" in sql

    def test_process_next_does_not_call_save_when_source_is_missing(self) -> None:
        from app.services.translation_jobs import process_next_job
        from app.services.translation_providers import FakeTranslationProvider

        conn = MagicMock()

        with (
            patch(f"{_REPO}.lock_next_pending_job", return_value=_job(JOB_ID_1)),
            patch(f"{_REPO}.get_translation_unit_for_job", return_value=None),
            patch(f"{_REPO}.save_translation_variant") as mock_save,
            patch(f"{_REPO}.mark_job_failed", return_value={}),
        ):
            result = process_next_job(conn, "worker", "en", FakeTranslationProvider())

        assert result is not None
        assert result["status"] == "failed"
        mock_save.assert_not_called()

    def test_fake_output_is_never_is_original(self) -> None:
        from app.services.translation_jobs import process_next_job
        from app.services.translation_providers import FakeTranslationProvider

        conn = MagicMock()
        unit = _unit()
        variant = _variant()

        with (
            patch(f"{_REPO}.lock_next_pending_job", return_value=_job(JOB_ID_1)),
            patch(f"{_REPO}.get_translation_unit_for_job", return_value=unit),
            patch(
                f"{_REPO}.save_translation_variant", return_value=variant
            ) as mock_save,
            patch(f"{_REPO}.mark_job_completed", return_value={}),
        ):
            process_next_job(conn, "worker", "en", FakeTranslationProvider())

        kwargs = mock_save.call_args.kwargs
        assert kwargs.get("locale_code") == "en"
        assert "[FAKE en]" in kwargs.get("text", "")
        assert kwargs.get("provider") == "fake"


class TestDiagnosticScriptImportable:
    def test_script_exists_and_is_runnable(self) -> None:
        from pathlib import Path

        script = (
            Path(__file__).parent.parent / "scripts" / "translation_pipeline_status.py"
        )
        assert script.exists(), f"diagnostic script not found at {script}"

    def test_script_has_main_function(self) -> None:
        import importlib.util
        from pathlib import Path

        script = (
            Path(__file__).parent.parent / "scripts" / "translation_pipeline_status.py"
        )
        spec = importlib.util.spec_from_file_location(
            "translation_pipeline_status", script
        )
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        assert hasattr(spec, "loader") and spec.loader is not None
        loader = spec.loader
        assert loader is not None
        loader.exec_module(module)
        assert hasattr(module, "main")
        assert callable(module.main)
