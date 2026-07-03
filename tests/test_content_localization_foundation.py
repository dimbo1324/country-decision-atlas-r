from app.repositories import translations as translation_repository
from app.services.localization import resolve_localized_text
from app.services.translation_hashing import calculate_source_hash
from app.services.translation_quality import build_translation_quality_results
from pathlib import Path
from psycopg import Connection
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())
MIGRATION_SQL = Path(
    "database/migrations/011_localization.sql"
).read_text(encoding="utf-8")


def test_localization_migration_extends_locale_foundation() -> None:
    for value in [
        "is_default",
        "fallback_locale_code",
        "direction",
        "locales_direction_check",
        "^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$",
        "('ru', 'Russian', 'Русский', TRUE, TRUE, 'ltr')",
        "('en', 'English', 'English', TRUE, FALSE, 'ltr')",
    ]:
        assert value in MIGRATION_SQL


def test_localization_migration_creates_units_variants_and_stale_view() -> None:
    for value in [
        "CREATE TABLE IF NOT EXISTS translation_units",
        "CREATE TABLE IF NOT EXISTS translation_variants",
        "ADD COLUMN IF NOT EXISTS translation_unit_id",
        "CREATE OR REPLACE VIEW stale_translation_variants",
        "source_hash",
        "ENCODE(DIGEST(ru_text, 'sha256'), 'hex')",
    ]:
        assert value in MIGRATION_SQL


def test_localization_migration_registers_critical_content() -> None:
    for entity_type in [
        "country_card",
        "legal_signal",
        "evidence_item",
        "source",
        "scenario",
        "country_score",
        "country_score_breakdown",
        "user_story",
    ]:
        assert f"'{entity_type}'" in MIGRATION_SQL
    for field_name in [
        "executive_summary",
        "title",
        "summary",
        "claim",
        "excerpt",
        "description",
        "explanation",
        "legal_path",
    ]:
        assert f"'{field_name}'" in MIGRATION_SQL


def test_source_hash_uses_sha256() -> None:
    assert calculate_source_hash("Русский оригинал") == (
        "a88deb482a56e049b48d05bcc233f77dd36daf459925c28550d97938dd2f11df"
    )


def test_localization_service_resolves_ru_original(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        translation_repository,
        "get_best_translation_variant",
        lambda *_: {
            "locale_code": "ru",
            "text": "Оригинал",
            "status": "original",
            "method": "legacy",
            "source_locale_code": "ru",
            "source_hash": "hash",
            "unit_source_hash": "hash",
            "is_original": True,
            "quality_score": None,
        },
    )

    result = resolve_localized_text(
        CONNECTION,
        "legal_signal",
        "entity-id",
        "title",
        "ru",
    )

    assert result is not None
    assert result.text == "Оригинал"
    assert result.meta.resolved_locale == "ru"
    assert result.meta.is_original is True
    assert result.meta.is_fallback is False


def test_localization_service_falls_back_to_ru(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        translation_repository,
        "get_best_translation_variant",
        lambda *_: {
            "locale_code": "ru",
            "text": "Резервный оригинал",
            "status": "original",
            "method": "legacy",
            "source_locale_code": "ru",
            "source_hash": "hash",
            "unit_source_hash": "hash",
            "is_original": True,
            "quality_score": 100,
        },
    )

    result = resolve_localized_text(
        CONNECTION,
        "legal_signal",
        "entity-id",
        "summary",
        "en",
    )

    assert result is not None
    assert result.meta.requested_locale == "en"
    assert result.meta.resolved_locale == "ru"
    assert result.meta.status == "fallback"
    assert result.meta.is_fallback is True


def install_quality_fakes(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        translation_repository,
        "list_foundation_locales",
        lambda *_: [
            {
                "code": "en",
                "is_active": True,
                "is_default": False,
                "fallback_locale_code": "ru",
                "direction": "ltr",
            },
            {
                "code": "ru",
                "is_active": True,
                "is_default": True,
                "fallback_locale_code": None,
                "direction": "ltr",
            },
        ],
    )
    monkeypatch.setattr(translation_repository, "count_default_locales", lambda *_: 1)
    monkeypatch.setattr(translation_repository, "count_translation_units", lambda *_: 1)
    monkeypatch.setattr(
        translation_repository, "count_translation_variants", lambda *_: 2
    )
    for name in [
        "list_critical_content_without_units",
        "list_active_units_without_variants",
        "list_units_without_original_variant",
        "list_original_variant_mismatches",
        "list_units_without_english_variant",
        "list_stale_translation_variants",
        "list_invalid_reviewed_machine_variants",
        "list_persisted_fallback_variants",
    ]:
        monkeypatch.setattr(translation_repository, name, lambda *_: [])


def test_translation_quality_foundation_is_valid(monkeypatch: Any) -> None:
    install_quality_fakes(monkeypatch)

    checks, issues = build_translation_quality_results(CONNECTION)

    assert issues == []
    assert checks
    assert all(check.status == "passed" for check in checks)


def test_translation_quality_detects_stale_variant(monkeypatch: Any) -> None:
    install_quality_fakes(monkeypatch)
    monkeypatch.setattr(
        translation_repository,
        "list_stale_translation_variants",
        lambda *_: [
            {
                "id": "variant-id",
                "translation_unit_id": "unit-id",
                "locale_code": "en",
            }
        ],
    )

    checks, issues = build_translation_quality_results(CONNECTION)

    assert any(issue.code == "translation_variant_stale" for issue in issues)
    assert any(
        check.code == "localization_stale_variants" and check.status == "failed"
        for check in checks
    )


def test_translation_quality_reports_missing_english_as_warning(
    monkeypatch: Any,
) -> None:
    install_quality_fakes(monkeypatch)
    monkeypatch.setattr(
        translation_repository,
        "list_units_without_english_variant",
        lambda *_: [
            {
                "id": "unit-id",
                "entity_type": "evidence_item",
                "entity_id": "entity-id",
                "field_name": "claim",
            }
        ],
    )

    checks, issues = build_translation_quality_results(CONNECTION)

    missing_issue = next(
        issue for issue in issues if issue.code == "translation_english_variant_missing"
    )
    assert missing_issue.severity == "warning"
    assert any(
        check.code == "localization_english_coverage" and check.status == "failed"
        for check in checks
    )
