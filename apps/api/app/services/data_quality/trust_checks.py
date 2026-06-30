from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_trust_surface_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_active_countries_missing_trust_scores(connection):
        issues.append(
            _issue(
                "trust_score_missing_for_active_country",
                "critical",
                "country_trust_score",
                row.get("slug"),
                "Active country has no trust score computed.",
                row,
            )
        )
    checks.append(
        _check(
            "all_active_countries_have_trust_scores",
            issues,
            ["trust_score_missing_for_active_country"],
        )
    )
    for row in repository.list_invalid_trust_score_values(connection):
        issues.append(
            _issue(
                "trust_score_value_invalid",
                "critical",
                "country_trust_score",
                row.get("id"),
                "Country trust score has invalid value, label, confidence, or freshness_status.",
                row,
            )
        )
    checks.append(
        _check(
            "trust_score_values_are_valid",
            issues,
            ["trust_score_value_invalid"],
        )
    )
    for row in repository.list_inconsistent_trust_insufficient_data(connection):
        issues.append(
            _issue(
                "trust_score_insufficient_data_inconsistent",
                "critical",
                "country_trust_score",
                row.get("id"),
                "Trust label is insufficient_data but trust_score is not NULL, or vice versa.",
                row,
            )
        )
    checks.append(
        _check(
            "trust_score_insufficient_data_is_consistent",
            issues,
            ["trust_score_insufficient_data_inconsistent"],
        )
    )
    for row in repository.list_stale_trust_scores(connection):
        issues.append(
            _issue(
                "trust_score_stale",
                "warning",
                "country_trust_score",
                row.get("id"),
                "Trust score has not been recomputed in over 30 days.",
                row,
            )
        )
    checks.append(
        _check(
            "trust_scores_are_fresh",
            issues,
            ["trust_score_stale"],
        )
    )
    for row in repository.list_missing_required_methodology_sections(connection):
        issues.append(
            _issue(
                "methodology_section_missing",
                "critical",
                "methodology_section",
                row.get("slug"),
                "Required methodology section is missing or not published.",
                row,
            )
        )
    checks.append(
        _check(
            "required_methodology_sections_exist",
            issues,
            ["methodology_section_missing"],
        )
    )
    for row in repository.list_missing_required_glossary_terms(connection):
        issues.append(
            _issue(
                "glossary_term_missing",
                "critical",
                "glossary_term",
                row.get("slug"),
                "Required glossary term is missing or not published.",
                row,
            )
        )
    checks.append(
        _check(
            "required_glossary_terms_exist",
            issues,
            ["glossary_term_missing"],
        )
    )
