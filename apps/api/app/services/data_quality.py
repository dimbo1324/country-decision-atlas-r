from app.core.errors import api_error
from app.repositories import data_quality as repository
from app.schemas.data_quality import (
    DataQualityCheck,
    DataQualityIssue,
    DataQualityReport,
)
from psycopg import Connection
from typing import Any


COUNTRY_CARD_FIELDS = [
    "executive_summary",
    "migration_overview",
    "tax_overview",
    "cost_of_living_overview",
    "business_overview",
    "safety_overview",
    "legal_signals_summary",
    "risk_summary",
    "source_summary",
]


def build_data_quality_report(connection: Connection[Any]) -> DataQualityReport:
    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    for row in repository.list_missing_mvp_countries(connection):
        issues.append(
            _issue(
                "mvp_country_missing",
                "critical",
                "country",
                None,
                "Required MVP country is missing or inactive.",
                row,
            )
        )
    checks.append(_check("mvp_countries_exist", issues, ["mvp_country_missing"]))
    for row in repository.list_published_countries_without_cards(connection):
        issues.append(
            _issue(
                "country_card_missing",
                "critical",
                "country",
                row.get("id"),
                "Published MVP country has no published EN country card.",
                row,
            )
        )
    checks.append(_check("mvp_countries_have_cards", issues, ["country_card_missing"]))
    for row in repository.list_published_countries_without_sources(connection):
        issues.append(
            _issue(
                "country_sources_missing",
                "critical",
                "country",
                row.get("id"),
                "Published MVP country has no published sources.",
                row,
            )
        )
    checks.append(
        _check("mvp_countries_have_sources", issues, ["country_sources_missing"])
    )
    for row in repository.list_missing_country_scores_for_required_scenarios(
        connection
    ):
        issues.append(
            _issue(
                "country_score_missing",
                "critical",
                "country_score",
                None,
                "Country score is missing for required MVP scenario.",
                row,
            )
        )
    checks.append(
        _check("mvp_country_scores_complete", issues, ["country_score_missing"])
    )
    for row in repository.list_scores_without_breakdowns(connection):
        issues.append(
            _issue(
                "score_breakdown_missing",
                "critical",
                "country_score",
                row.get("country_score_id"),
                "Country score has no breakdown rows.",
                row,
            )
        )
    for row in repository.list_scores_with_incomplete_breakdowns(connection):
        issues.append(
            _issue(
                "score_breakdown_count_invalid",
                "critical",
                "country_score",
                row.get("country_score_id"),
                "Country score must have exactly 7 breakdown rows.",
                row,
            )
        )
    for row in repository.list_scores_with_invalid_weight_sum(connection):
        issues.append(
            _issue(
                "score_breakdown_weight_sum_invalid",
                "critical",
                "country_score",
                row.get("country_score_id"),
                "Country score breakdown weights must sum to expected total.",
                row,
            )
        )
    checks.append(
        _check(
            "mvp_score_breakdowns_complete",
            issues,
            [
                "score_breakdown_missing",
                "score_breakdown_count_invalid",
                "score_breakdown_weight_sum_invalid",
            ],
        )
    )
    for row in repository.list_published_legal_signals_without_source(connection):
        issues.append(
            _issue(
                "published_legal_signal_source_missing",
                "critical",
                "legal_signal",
                row.get("id"),
                "Published legal signal has no source.",
                row,
            )
        )
    checks.append(
        _check(
            "published_legal_signals_have_sources",
            issues,
            ["published_legal_signal_source_missing"],
        )
    )
    for row in repository.list_published_legal_signals_without_evidence(connection):
        issues.append(
            _issue(
                "published_legal_signal_evidence_missing",
                "warning",
                "legal_signal",
                row.get("id"),
                "Published legal signal has no evidence item.",
                row,
            )
        )
    checks.append(
        _check(
            "published_legal_signals_have_evidence",
            issues,
            ["published_legal_signal_evidence_missing"],
        )
    )
    for row in repository.list_evidence_without_source(connection):
        issues.append(
            _issue(
                "evidence_source_missing",
                "critical",
                "evidence_item",
                row.get("id"),
                "Evidence item has no source.",
                row,
            )
        )
    for row in repository.list_evidence_without_country(connection):
        issues.append(
            _issue(
                "evidence_country_missing",
                "critical",
                "evidence_item",
                row.get("id"),
                "Evidence item has no country.",
                row,
            )
        )
    checks.append(
        _check(
            "evidence_is_traceable",
            issues,
            ["evidence_source_missing", "evidence_country_missing"],
        )
    )
    for row in repository.list_published_sources_with_missing_required_fields(
        connection
    ):
        issues.append(
            _issue(
                "published_source_required_field_missing",
                "critical",
                "source",
                row.get("id"),
                "Published source is missing required field.",
                row,
            )
        )
    checks.append(
        _check(
            "published_sources_have_required_fields",
            issues,
            ["published_source_required_field_missing"],
        )
    )
    for row in repository.list_invalid_synthetic_user_stories(connection):
        issues.append(
            _issue(
                "synthetic_user_story_invalid",
                "critical",
                "user_story",
                row.get("id"),
                "Synthetic user story must not look like a verified real story.",
                row,
            )
        )
    checks.append(
        _check(
            "synthetic_user_stories_are_marked",
            issues,
            ["synthetic_user_story_invalid"],
        )
    )
    for row in repository.list_country_cards_with_empty_major_sections(connection):
        issues.append(
            _issue(
                "country_card_section_missing",
                "critical",
                "country_card",
                row.get("id"),
                "Published country card has empty major public sections.",
                row,
            )
        )
    checks.append(
        _check(
            "country_cards_have_public_sections",
            issues,
            ["country_card_section_missing"],
        )
    )
    critical_issues_count = sum(1 for issue in issues if issue.severity == "critical")
    warnings_count = sum(1 for issue in issues if issue.severity == "warning")
    return DataQualityReport(
        overall_status="valid" if critical_issues_count == 0 else "invalid",
        valid=critical_issues_count == 0,
        critical_issues_count=critical_issues_count,
        warnings_count=warnings_count,
        checks=checks,
        issues=issues,
    )


def validate_source_for_publish(source: dict[str, Any]) -> list[DataQualityIssue]:
    issues = _required_field_issues(
        source,
        "source",
        ["title", "url", "publisher", "source_type"],
        "source_required_field_missing",
        "Published source is missing required field.",
    )
    if _missing(source.get("confidence")) and _missing(source.get("reliability_level")):
        issues.append(
            _issue(
                "source_confidence_missing",
                "critical",
                "source",
                source.get("id"),
                "Published source is missing confidence/reliability level.",
                {"field": "confidence"},
            )
        )
    return issues


def validate_legal_signal_for_publish(
    legal_signal: dict[str, Any],
) -> list[DataQualityIssue]:
    issues = _required_field_issues(
        legal_signal,
        "legal_signal",
        [
            "country_id",
            "source_id",
            "signal_type",
            "impact_direction",
            "impact_level",
        ],
        "legal_signal_required_field_missing",
        "Published legal signal is missing required field.",
    )
    if _missing(legal_signal.get("title_en")) and _missing(legal_signal.get("title")):
        issues.append(_missing_field_issue(legal_signal, "legal_signal", "title_en"))
    if _missing(legal_signal.get("summary_en")) and _missing(
        legal_signal.get("summary")
    ):
        issues.append(_missing_field_issue(legal_signal, "legal_signal", "summary_en"))
    if _missing(legal_signal.get("confidence")) and _missing(
        legal_signal.get("confidence_level")
    ):
        issues.append(_missing_field_issue(legal_signal, "legal_signal", "confidence"))
    return issues


def validate_evidence_item_for_publish(
    evidence_item: dict[str, Any],
) -> list[DataQualityIssue]:
    issues = _required_field_issues(
        evidence_item,
        "evidence_item",
        ["source_id", "country_id"],
        "evidence_required_field_missing",
        "Published evidence item is missing required field.",
    )
    if _missing(evidence_item.get("claim")) and _missing(evidence_item.get("title")):
        issues.append(_missing_field_issue(evidence_item, "evidence_item", "claim"))
    if _missing(evidence_item.get("confidence")) and _missing(
        evidence_item.get("confidence_level")
    ):
        issues.append(
            _missing_field_issue(evidence_item, "evidence_item", "confidence")
        )
    if (
        _missing(evidence_item.get("url"))
        and _missing(evidence_item.get("excerpt"))
        and _missing(evidence_item.get("quote"))
    ):
        issues.append(_missing_field_issue(evidence_item, "evidence_item", "excerpt"))
    return issues


def validate_country_card_for_publish(
    country_card: dict[str, Any],
) -> list[DataQualityIssue]:
    if any(not _missing(country_card.get(field)) for field in COUNTRY_CARD_FIELDS):
        return []
    return [
        _issue(
            "country_card_public_text_missing",
            "critical",
            "country_card",
            country_card.get("id"),
            "Country card cannot be published because public text is empty.",
            {"fields": COUNTRY_CARD_FIELDS},
        )
    ]


def validate_user_story_for_publish(
    user_story: dict[str, Any],
) -> list[DataQualityIssue]:
    issues = _required_field_issues(
        user_story,
        "user_story",
        ["origin_country_id", "destination_country_id", "scenario", "year"],
        "user_story_required_field_missing",
        "Published user story is missing required field.",
    )
    if user_story.get("verification_status") == "verified":
        issues.append(
            _issue(
                "user_story_verified_without_verification",
                "critical",
                "user_story",
                user_story.get("id"),
                "User story cannot be marked verified without verification workflow.",
                {"verification_status": user_story.get("verification_status")},
            )
        )
    if user_story.get("is_synthetic"):
        notes = str(user_story.get("notes") or "").lower()
        if user_story.get("verification_status") != "synthetic" or not (
            "synthetic" in notes or "demo" in notes
        ):
            issues.append(
                _issue(
                    "synthetic_user_story_invalid",
                    "critical",
                    "user_story",
                    user_story.get("id"),
                    "Synthetic user story must not look like a verified real story.",
                    {
                        "verification_status": user_story.get("verification_status"),
                        "notes": user_story.get("notes"),
                    },
                )
            )
    return issues


def raise_if_critical_issues(issues: list[DataQualityIssue]) -> None:
    critical_issues = [issue for issue in issues if issue.severity == "critical"]
    if critical_issues:
        raise api_error(
            422,
            "data_quality_validation_failed",
            "Content cannot be published because data quality checks failed.",
            {"issues": [issue.model_dump(mode="json") for issue in critical_issues]},
        )


def _required_field_issues(
    data: dict[str, Any],
    entity_type: str,
    fields: list[str],
    code: str,
    message: str,
) -> list[DataQualityIssue]:
    return [
        _issue(
            code,
            "critical",
            entity_type,
            data.get("id"),
            message,
            {"field": field},
        )
        for field in fields
        if _missing(data.get(field))
    ]


def _missing_field_issue(
    data: dict[str, Any], entity_type: str, field: str
) -> DataQualityIssue:
    return _issue(
        f"{entity_type}_required_field_missing",
        "critical",
        entity_type,
        data.get("id"),
        f"Published {entity_type} is missing required field.",
        {"field": field},
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


def _missing(value: Any) -> bool:
    return value is None or value == ""


def _check(
    code: str, issues: list[DataQualityIssue], issue_codes: list[str]
) -> DataQualityCheck:
    failed = any(issue.code in issue_codes for issue in issues)
    return DataQualityCheck(code=code, status="failed" if failed else "passed")
