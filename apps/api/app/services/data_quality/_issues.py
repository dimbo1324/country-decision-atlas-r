from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
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
