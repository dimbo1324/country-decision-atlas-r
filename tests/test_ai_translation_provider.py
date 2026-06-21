from __future__ import annotations

import os
import pytest
from typing import Any
from unittest.mock import MagicMock, patch


UNIT_ID = "00000000-0000-0000-0000-000000000001"
VARIANT_ID = "00000000-0000-0000-0000-000000000002"
JOB_ID = "00000000-0000-0000-0000-000000000003"
_REPO = "app.repositories.translation_jobs"


def _make_conn() -> Any:
    return MagicMock()


def _job(status: str = "processing", attempts: int = 1) -> dict[str, Any]:
    from datetime import UTC, datetime

    return {
        "id": JOB_ID,
        "translation_unit_id": UNIT_ID,
        "source_locale_code": "ru",
        "target_locale_code": "en",
        "status": status,
        "priority": 100,
        "attempts": attempts,
        "max_attempts": 3,
        "provider": None,
        "provider_model": None,
        "error_message": None,
        "locked_at": None,
        "locked_by": "worker-1",
        "metadata": {},
        "created_at": datetime.now(UTC),
        "started_at": None,
        "completed_at": None,
        "failed_at": None,
        "updated_at": datetime.now(UTC),
    }


def _unit(source_text: str = "Привет мир") -> dict[str, Any]:
    return {
        "id": UNIT_ID,
        "original_locale_code": "ru",
        "source_hash": "abc123",
        "source_text": source_text,
    }


def _variant(text: str = "[FAKE en] Привет мир") -> dict[str, Any]:
    return {
        "id": VARIANT_ID,
        "locale_code": "en",
        "text": text,
        "status": "machine_translated",
        "method": "machine",
        "is_original": False,
        "source_hash": "abc123",
    }


class TestTranslationInput:
    def test_input_model_defaults(self) -> None:
        from app.services.translation_providers import TranslationInput

        inp = TranslationInput(
            source_text="Hello", source_locale="ru", target_locale="en"
        )
        assert inp.domain == "legal_migration"
        assert inp.glossary_terms is None
        assert inp.entity_type is None

    def test_input_with_glossary(self) -> None:
        from app.services.translation_providers import TranslationInput

        inp = TranslationInput(
            source_text="ВНЖ",
            source_locale="ru",
            target_locale="en",
            glossary_terms={"ВНЖ": "residence permit"},
        )
        assert inp.glossary_terms == {"ВНЖ": "residence permit"}


class TestFakeProviderNewInterface:
    def test_fake_accepts_translation_input(self) -> None:
        from app.services.translation_providers import (
            FakeTranslationProvider,
            TranslationInput,
        )

        provider = FakeTranslationProvider()
        inp = TranslationInput(
            source_text="Тест", source_locale="ru", target_locale="en"
        )
        result = provider.translate(inp)
        assert result.text == "[FAKE en] Тест"
        assert result.provider == "fake"
        assert result.provider_model == "fake-v1"
        assert result.input_chars == 4
        assert result.duration_ms == 1

    def test_fake_includes_input_output_chars(self) -> None:
        from app.services.translation_providers import (
            FakeTranslationProvider,
            TranslationInput,
        )

        provider = FakeTranslationProvider()
        inp = TranslationInput(
            source_text="Hello", source_locale="en", target_locale="de"
        )
        result = provider.translate(inp)
        assert result.input_chars == 5
        assert result.output_chars is not None


class TestAITranslationProvider:
    def test_ai_provider_calls_openai_endpoint(self) -> None:
        from app.services.translation_providers import (
            AITranslationProvider,
            TranslationInput,
        )

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello world"}}],
            "usage": {"prompt_tokens": 50, "completion_tokens": 10, "total_tokens": 60},
        }
        mock_response.headers = {"x-request-id": "req-123"}
        mock_response.raise_for_status = MagicMock()

        provider = AITranslationProvider(api_key="sk-test", model="gpt-4o-mini")
        inp = TranslationInput(
            source_text="Привет мир", source_locale="ru", target_locale="en"
        )

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            result = provider.translate(inp)

        assert result.text == "Hello world"
        assert result.provider == "openai"
        assert result.provider_model == "gpt-4o-mini"
        assert result.raw_metadata is not None
        assert result.raw_metadata["total_tokens"] == 60
        assert result.raw_metadata["request_id"] == "req-123"

    def test_ai_provider_retries_on_failure(self) -> None:
        from app.services.translation_providers import (
            AITranslationProvider,
            TranslationInput,
        )

        provider = AITranslationProvider(
            api_key="sk-test", model="gpt-4o-mini", max_retries=1
        )
        inp = TranslationInput(
            source_text="test", source_locale="ru", target_locale="en"
        )

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = [
                RuntimeError("timeout"),
                RuntimeError("timeout"),
            ]
            mock_client_cls.return_value = mock_client

            with patch("time.sleep"), pytest.raises(RuntimeError, match="failed after"):
                provider.translate(inp)

        assert mock_client.post.call_count == 2

    def test_ai_provider_system_prompt_contains_glossary(self) -> None:
        from app.services.translation_providers import (
            AITranslationProvider,
            TranslationInput,
        )

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "residence permit"}}],
            "usage": {},
        }
        mock_response.headers = {}
        mock_response.raise_for_status = MagicMock()

        provider = AITranslationProvider(api_key="sk-test")
        inp = TranslationInput(
            source_text="ВНЖ",
            source_locale="ru",
            target_locale="en",
            glossary_terms={"ВНЖ": "residence permit"},
        )

        captured_payload: list[Any] = []
        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)

            def _capture(_url: str, **kwargs: Any) -> Any:
                captured_payload.append(kwargs.get("json", {}))
                return mock_response

            mock_client.post.side_effect = _capture
            mock_client_cls.return_value = mock_client
            provider.translate(inp)

        assert len(captured_payload) == 1
        system_msg = captured_payload[0]["messages"][0]["content"]
        assert "ВНЖ" in system_msg
        assert "residence permit" in system_msg


class TestProviderFactory:
    def test_factory_returns_fake_by_default(self) -> None:
        from app.core.config import get_settings
        from app.services.translation_providers import (
            FakeTranslationProvider,
            get_translation_provider,
        )

        get_settings.cache_clear()
        os.environ["TRANSLATION_PROVIDER"] = "fake"
        get_settings.cache_clear()
        try:
            provider = get_translation_provider()
            assert isinstance(provider, FakeTranslationProvider)
        finally:
            os.environ.pop("TRANSLATION_PROVIDER", None)
            get_settings.cache_clear()

    def test_factory_returns_ai_when_configured(self) -> None:
        from app.core.config import get_settings
        from app.services.translation_providers import (
            AITranslationProvider,
            get_translation_provider,
        )

        get_settings.cache_clear()
        os.environ["TRANSLATION_PROVIDER"] = "ai"
        os.environ["AI_TRANSLATION_PROVIDER"] = "openai"
        os.environ["AI_TRANSLATION_API_KEY"] = "sk-test-key"
        get_settings.cache_clear()
        try:
            provider = get_translation_provider()
            assert isinstance(provider, AITranslationProvider)
        finally:
            os.environ.pop("TRANSLATION_PROVIDER", None)
            os.environ.pop("AI_TRANSLATION_PROVIDER", None)
            os.environ.pop("AI_TRANSLATION_API_KEY", None)
            get_settings.cache_clear()

    def test_factory_raises_when_ai_key_missing(self) -> None:
        from app.core.config import get_settings
        from app.services.translation_providers import get_translation_provider

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


class TestTranslationValidation:
    def test_valid_translation_passes(self) -> None:
        from app.services.translation_validation import validate_translation

        ok, err = validate_translation("Привет мир", "Hello world", "ru", "en")
        assert ok is True
        assert err is None

    def test_empty_translation_fails(self) -> None:
        from app.services.translation_validation import validate_translation

        ok, err = validate_translation("Hello", "", "ru", "en")
        assert ok is False
        assert err is not None

    def test_whitespace_only_fails(self) -> None:
        from app.services.translation_validation import validate_translation

        ok, _ = validate_translation("Hello", "   ", "ru", "en")
        assert ok is False

    def test_identical_text_different_locale_fails(self) -> None:
        from app.services.translation_validation import validate_translation

        ok, err = validate_translation("Hello world", "Hello world", "ru", "en")
        assert ok is False
        assert err is not None

    def test_identical_text_same_locale_passes(self) -> None:
        from app.services.translation_validation import validate_translation

        ok, _ = validate_translation("Hello", "Hello", "en", "en")
        assert ok is True

    def test_ai_noise_rejected(self) -> None:
        from app.services.translation_validation import validate_translation

        ok, _ = validate_translation(
            "text", "As an AI language model, I cannot...", "ru", "en"
        )
        assert ok is False

    def test_suspiciously_long_rejected(self) -> None:
        from app.services.translation_validation import validate_translation

        ok, _ = validate_translation("Hi", "x" * 300, "ru", "en")
        assert ok is False

    def test_missing_important_number_rejected(self) -> None:
        from app.services.translation_validation import validate_translation

        ok, err = validate_translation(
            "Согласно статье 12345 закона",
            "According to the article of the law",
            "ru",
            "en",
        )
        assert ok is False
        assert "12345" in (err or "")

    def test_important_number_preserved_passes(self) -> None:
        from app.services.translation_validation import validate_translation

        ok, _ = validate_translation(
            "Статья 12345 налогового кодекса",
            "Article 12345 of the tax code",
            "ru",
            "en",
        )
        assert ok is True


class TestProcessNextJobWithAI:
    def test_process_next_with_mocked_ai_provider(self) -> None:
        from app.services.translation_jobs import process_next_job
        from app.services.translation_providers import (
            TranslationInput,
            TranslationResult,
        )

        conn = _make_conn()
        processing_job = _job()
        unit_data = _unit()
        variant_data = _variant("Hello world")

        mock_provider = MagicMock()
        mock_provider.translate.return_value = TranslationResult(
            text="Hello world",
            provider="openai",
            provider_model="gpt-4o-mini",
            input_chars=10,
            output_chars=11,
            duration_ms=250,
        )

        with (
            patch(f"{_REPO}.lock_next_pending_job", return_value=processing_job),
            patch(f"{_REPO}.get_translation_unit_for_job", return_value=unit_data),
            patch(f"{_REPO}.save_translation_variant", return_value=variant_data),
            patch(f"{_REPO}.mark_job_completed", return_value={}),
        ):
            result = process_next_job(conn, "worker-1", "en", mock_provider)

        assert result is not None
        assert result["status"] == "completed"
        assert result["variant_id"] == VARIANT_ID
        mock_provider.translate.assert_called_once()
        call_arg = mock_provider.translate.call_args[0][0]
        assert isinstance(call_arg, TranslationInput)
        assert call_arg.source_text == "Привет мир"
        assert call_arg.target_locale == "en"

    def test_failed_provider_marks_job_failed(self) -> None:
        from app.services.translation_jobs import process_next_job

        conn = _make_conn()
        processing_job = _job()
        unit_data = _unit()

        mock_provider = MagicMock()
        mock_provider.translate.side_effect = RuntimeError("API timeout")

        with (
            patch(f"{_REPO}.lock_next_pending_job", return_value=processing_job),
            patch(f"{_REPO}.get_translation_unit_for_job", return_value=unit_data),
            patch(f"{_REPO}.mark_job_failed", return_value={}) as mock_fail,
        ):
            result = process_next_job(conn, "worker-1", "en", mock_provider)

        assert result is not None
        assert result["status"] == "failed"
        assert "API timeout" in (result.get("error") or "")
        mock_fail.assert_called_once()

    def test_validation_failure_marks_job_failed(self) -> None:
        from app.services.translation_jobs import process_next_job
        from app.services.translation_providers import TranslationResult

        conn = _make_conn()
        processing_job = _job()
        unit_data = _unit("Привет мир")

        mock_provider = MagicMock()
        mock_provider.translate.return_value = TranslationResult(
            text="Привет мир",
            provider="openai",
            provider_model="gpt-4o-mini",
        )

        with (
            patch(f"{_REPO}.lock_next_pending_job", return_value=processing_job),
            patch(f"{_REPO}.get_translation_unit_for_job", return_value=unit_data),
            patch(f"{_REPO}.mark_job_failed", return_value={}) as mock_fail,
        ):
            result = process_next_job(conn, "worker-1", "en", mock_provider)

        assert result is not None
        assert result["status"] == "failed"
        assert "validation_failed" in (result.get("error") or "")
        mock_fail.assert_called_once()


class TestDryRun:
    def test_dry_run_returns_translated_text_without_saving(self) -> None:
        from app.services.translation_jobs import process_next_job
        from app.services.translation_providers import TranslationResult

        conn = _make_conn()
        processing_job = _job()
        unit_data = _unit()

        mock_provider = MagicMock()
        mock_provider.translate.return_value = TranslationResult(
            text="Hello world",
            provider="fake",
            provider_model="fake-v1",
        )

        with (
            patch(f"{_REPO}.lock_next_pending_job", return_value=processing_job),
            patch(f"{_REPO}.get_translation_unit_for_job", return_value=unit_data),
            patch(f"{_REPO}.save_translation_variant") as mock_save,
            patch(f"{_REPO}.mark_job_completed") as mock_complete,
        ):
            result = process_next_job(
                conn, "worker-1", "en", mock_provider, dry_run=True
            )

        assert result is not None
        assert result["status"] == "dry_run"
        assert result["variant_id"] is None
        assert result["translated_text"] == "Hello world"
        mock_save.assert_not_called()
        mock_complete.assert_not_called()

    def test_dry_run_does_not_persist_failure(self) -> None:
        from app.services.translation_jobs import process_next_job

        conn = _make_conn()
        processing_job = _job()
        unit_data = _unit()

        mock_provider = MagicMock()
        mock_provider.translate.side_effect = RuntimeError("boom")

        with (
            patch(f"{_REPO}.lock_next_pending_job", return_value=processing_job),
            patch(f"{_REPO}.get_translation_unit_for_job", return_value=unit_data),
            patch(f"{_REPO}.mark_job_failed") as mock_fail,
        ):
            result = process_next_job(
                conn, "worker-1", "en", mock_provider, dry_run=True
            )

        assert result is not None
        assert result["status"] == "failed"
        mock_fail.assert_not_called()

    def test_process_batch_dry_run_counts_correctly(self) -> None:
        from app.services.translation_jobs import process_batch
        from app.services.translation_providers import TranslationResult

        conn = _make_conn()

        mock_provider = MagicMock()
        mock_provider.translate.return_value = TranslationResult(
            text="Hello world",
            provider="fake",
            provider_model="fake-v1",
        )

        dry_run_result: dict[str, Any] = {
            "job_id": JOB_ID,
            "status": "dry_run",
            "target_locale_code": "en",
            "variant_id": None,
            "translated_text": "Hello world",
            "metadata": {},
        }

        with patch("app.services.translation_jobs.process_next_job") as mock_process:
            mock_process.side_effect = [dry_run_result, None]
            result = process_batch(
                conn, "worker-1", "en", 5, mock_provider, dry_run=True
            )

        assert result["processed"] == 1
        assert result["completed"] == 1
        assert result["failed"] == 0


class TestProviderMetadata:
    def test_metadata_included_in_result(self) -> None:
        from app.services.translation_jobs import process_next_job
        from app.services.translation_providers import TranslationResult

        conn = _make_conn()
        processing_job = _job()
        unit_data = _unit()
        variant_data = _variant("Hello world")

        mock_provider = MagicMock()
        mock_provider.translate.return_value = TranslationResult(
            text="Hello world",
            provider="openai",
            provider_model="gpt-4o-mini",
            input_chars=10,
            output_chars=11,
            duration_ms=321,
            raw_metadata={"total_tokens": 60},
        )

        with (
            patch(f"{_REPO}.lock_next_pending_job", return_value=processing_job),
            patch(f"{_REPO}.get_translation_unit_for_job", return_value=unit_data),
            patch(f"{_REPO}.save_translation_variant", return_value=variant_data),
            patch(f"{_REPO}.mark_job_completed", return_value={}),
        ):
            result = process_next_job(conn, "worker-1", "en", mock_provider)

        assert result is not None
        metadata = result.get("metadata") or {}
        assert metadata.get("provider") == "openai"
        assert metadata.get("duration_ms") == 321
        assert metadata.get("input_chars") == 10
        assert metadata.get("total_tokens") == 60


class TestRegressionAfterAIProvider:
    def test_countries_repo_still_importable(self) -> None:
        from app.repositories.countries import list_countries

        assert callable(list_countries)

    def test_localization_service_still_importable(self) -> None:
        from app.services.localization import overlay_localized_fields

        assert callable(overlay_localized_fields)

    def test_decision_engine_still_importable(self) -> None:
        from app.services.decision_engine import run_decision

        assert callable(run_decision)

    def test_translation_provider_interface_is_stable(self) -> None:
        from app.services.translation_providers import (
            AITranslationProvider,
            FakeTranslationProvider,
            TranslationProvider,
            get_translation_provider,
        )

        assert issubclass(FakeTranslationProvider, TranslationProvider)
        assert issubclass(AITranslationProvider, TranslationProvider)
        assert callable(get_translation_provider)

    def test_validation_module_importable(self) -> None:
        from app.services.translation_validation import validate_translation

        assert callable(validate_translation)

    def test_config_has_translation_provider_settings(self) -> None:
        from app.core.config import get_settings

        get_settings.cache_clear()
        settings = get_settings()
        assert hasattr(settings, "translation_provider")
        assert hasattr(settings, "ai_translation_model")
        get_settings.cache_clear()
