from app.repositories import translations as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from psycopg import Connection
from typing import Any


def build_translation_quality_results(
    connection: Connection[Any],
) -> tuple[list[DataQualityCheck], list[DataQualityIssue]]:
    checks: list[DataQualityCheck] = []
    issues: list[DataQualityIssue] = []
    locales = {
        row["code"]: row for row in repository.list_foundation_locales(connection)
    }
    for code in ("ru", "en"):
        locale = locales.get(code)
        if locale is None:
            issues.append(
                _issue(
                    "localization_locale_missing",
                    "critical",
                    "locale",
                    code,
                    "Required localization locale is missing.",
                    {"locale_code": code},
                )
            )
        elif not locale["is_active"]:
            issues.append(
                _issue(
                    "localization_locale_inactive",
                    "critical",
                    "locale",
                    code,
                    "Required localization locale is inactive.",
                    {"locale_code": code},
                )
            )
    checks.append(
        _check(
            "localization_locales_ready",
            issues,
            ["localization_locale_missing", "localization_locale_inactive"],
        )
    )
    default_count = repository.count_default_locales(connection)
    if default_count != 1 or not locales.get("ru", {}).get("is_default", False):
        issues.append(
            _issue(
                "localization_default_locale_invalid",
                "critical",
                "locale",
                None,
                "Localization requires exactly one default content locale set to ru.",
                {"default_locale_count": default_count},
            )
        )
    checks.append(
        _check(
            "localization_default_locale_ready",
            issues,
            ["localization_default_locale_invalid"],
        )
    )
    unit_count = repository.count_translation_units(connection)
    variant_count = repository.count_translation_variants(connection)
    if unit_count == 0:
        issues.append(
            _issue(
                "translation_units_empty",
                "critical",
                "translation_unit",
                None,
                "Content localization has no translation units.",
                {},
            )
        )
    if variant_count == 0:
        issues.append(
            _issue(
                "translation_variants_empty",
                "critical",
                "translation_variant",
                None,
                "Content localization has no translation variants.",
                {},
            )
        )
    for row in repository.list_critical_content_without_units(connection):
        issues.append(
            _row_issue(
                "critical_content_translation_unit_missing",
                "critical",
                row,
                "Critical localized content has no translation unit.",
            )
        )
    checks.append(
        _check(
            "localization_content_registered",
            issues,
            [
                "translation_units_empty",
                "translation_variants_empty",
                "critical_content_translation_unit_missing",
            ],
        )
    )
    for row in repository.list_active_units_without_variants(connection):
        issues.append(
            _row_issue(
                "translation_unit_without_variants",
                "critical",
                row,
                "Active translation unit has no variants.",
            )
        )
    for row in repository.list_units_without_original_variant(connection):
        issues.append(
            _row_issue(
                "translation_unit_without_original",
                "critical",
                row,
                "Translation unit has no original variant.",
            )
        )
    checks.append(
        _check(
            "localization_units_have_originals",
            issues,
            ["translation_unit_without_variants", "translation_unit_without_original"],
        )
    )
    for row in repository.list_original_variant_mismatches(connection):
        issues.append(
            _row_issue(
                "translation_original_mismatch",
                "critical",
                row,
                "Original variant locale or source hash does not match its unit.",
            )
        )
    checks.append(
        _check(
            "localization_originals_consistent",
            issues,
            ["translation_original_mismatch"],
        )
    )
    for row in repository.list_units_without_english_variant(connection):
        issues.append(
            _row_issue(
                "translation_english_variant_missing",
                "warning",
                row,
                "Translation unit has no current English variant.",
            )
        )
    checks.append(
        _check(
            "localization_english_coverage",
            issues,
            ["translation_english_variant_missing"],
        )
    )
    for row in repository.list_stale_translation_variants(connection):
        issues.append(
            _row_issue(
                "translation_variant_stale",
                "warning",
                row,
                "Translation variant was created from an outdated source hash.",
            )
        )
    checks.append(
        _check(
            "localization_stale_variants",
            issues,
            ["translation_variant_stale"],
        )
    )
    for row in repository.list_invalid_reviewed_machine_variants(connection):
        issues.append(
            _row_issue(
                "translation_machine_review_invalid",
                "warning",
                row,
                "Machine translation is marked reviewed without review metadata.",
            )
        )
    for row in repository.list_persisted_fallback_variants(connection):
        issues.append(
            _row_issue(
                "translation_fallback_persisted",
                "warning",
                row,
                "Fallback resolution was persisted as a translation variant.",
            )
        )
    checks.append(
        _check(
            "localization_variant_workflow_valid",
            issues,
            ["translation_machine_review_invalid", "translation_fallback_persisted"],
        )
    )
    return checks, issues


def _row_issue(
    code: str,
    severity: str,
    row: dict[str, Any],
    message: str,
) -> DataQualityIssue:
    return _issue(
        code,
        severity,
        "translation_unit",
        row.get("translation_unit_id") or row.get("id"),
        message,
        row,
    )


def _issue(
    code: str,
    severity: str,
    entity_type: str,
    entity_id: Any,
    message: str,
    details: dict[str, Any],
) -> DataQualityIssue:
    return DataQualityIssue(
        code=code,
        severity=severity,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        message=message,
        details={str(key): value for key, value in details.items()},
    )


def _check(
    code: str,
    issues: list[DataQualityIssue],
    issue_codes: list[str],
) -> DataQualityCheck:
    failed = any(issue.code in issue_codes for issue in issues)
    return DataQualityCheck(code=code, status="failed" if failed else "passed")
