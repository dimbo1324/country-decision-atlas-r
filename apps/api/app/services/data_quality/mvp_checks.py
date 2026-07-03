from app.repositories import data_quality as repository
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_mvp_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
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
    for row in repository.list_mvp_countries_with_too_few_published_sources(connection):
        issues.append(
            _issue(
                "mvp_country_published_source_count_low",
                "accepted_mvp_warning",
                "country",
                row.get("id"),
                "Published MVP country is below the future source-depth target.",
                {**row, "classification": "future_scope"},
            )
        )
    for row in repository.list_mvp_countries_with_too_few_published_evidence(
        connection
    ):
        issues.append(
            _issue(
                "mvp_country_published_evidence_count_low",
                "accepted_mvp_warning",
                "country",
                row.get("id"),
                "Published MVP country is below the future evidence-depth target.",
                {**row, "classification": "future_scope"},
            )
        )
    for row in repository.list_mvp_countries_with_too_few_published_legal_signals(
        connection
    ):
        issues.append(
            _issue(
                "mvp_country_published_legal_signal_count_low",
                "accepted_mvp_warning",
                "country",
                row.get("id"),
                "Published MVP country is below the future legal-signal depth target.",
                {**row, "classification": "future_scope"},
            )
        )
    checks.append(
        _check(
            "mvp_country_content_depth",
            issues,
            [
                "mvp_country_published_source_count_low",
                "mvp_country_published_evidence_count_low",
                "mvp_country_published_legal_signal_count_low",
            ],
        )
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
    for row in repository.list_inactive_mvp_scenarios(connection):
        issues.append(
            _issue(
                "mvp_scenario_inactive",
                "critical",
                "scenario",
                None,
                "Required MVP scenario is missing or inactive.",
                row,
            )
        )
    checks.append(_check("mvp_scenarios_active", issues, ["mvp_scenario_inactive"]))
