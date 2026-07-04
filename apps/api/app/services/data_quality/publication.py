from app.core.errors import api_error
from app.schemas.data_quality import DataQualityIssue
from app.services.data_quality._issues import (
    COUNTRY_CARD_FIELDS,
    _issue,
    _missing,
    _missing_field_issue,
    _required_field_issues,
)
from typing import Any


def validate_source_for_publish(
    source: dict[str, Any],
) -> list[DataQualityIssue]:
    issues = _required_field_issues(
        source,
        "source",
        ["title", "url", "publisher", "source_type"],
        "source_required_field_missing",
        "Published source is missing required field.",
    )
    if _missing(source.get("confidence")) and _missing(
        source.get("reliability_level")
    ):
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
    if _missing(legal_signal.get("title_en")) and _missing(
        legal_signal.get("title")
    ):
        issues.append(
            _missing_field_issue(legal_signal, "legal_signal", "title_en")
        )
    if _missing(legal_signal.get("summary_en")) and _missing(
        legal_signal.get("summary")
    ):
        issues.append(
            _missing_field_issue(legal_signal, "legal_signal", "summary_en")
        )
    if _missing(legal_signal.get("confidence")) and _missing(
        legal_signal.get("confidence_level")
    ):
        issues.append(
            _missing_field_issue(legal_signal, "legal_signal", "confidence")
        )
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
    if _missing(evidence_item.get("claim")) and _missing(
        evidence_item.get("title")
    ):
        issues.append(
            _missing_field_issue(evidence_item, "evidence_item", "claim")
        )
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
        issues.append(
            _missing_field_issue(evidence_item, "evidence_item", "excerpt")
        )
    return issues


def validate_country_card_for_publish(
    country_card: dict[str, Any],
) -> list[DataQualityIssue]:
    if any(
        not _missing(country_card.get(field)) for field in COUNTRY_CARD_FIELDS
    ):
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
                        "verification_status": user_story.get(
                            "verification_status"
                        ),
                        "notes": user_story.get("notes"),
                    },
                )
            )
    return issues


def raise_if_critical_issues(issues: list[DataQualityIssue]) -> None:
    critical_issues = [
        issue for issue in issues if issue.severity == "critical"
    ]
    if critical_issues:
        raise api_error(
            422,
            "data_quality_validation_failed",
            "Content cannot be published because data quality checks failed.",
            {
                "issues": [
                    issue.model_dump(mode="json") for issue in critical_issues
                ]
            },
        )
