from app.repositories import country_onboarding as repository
from app.repositories.data_quality import (
    MVP_COUNTRY_SLUGS,
    MVP_SCENARIO_SLUGS,
    ONBOARDING_COUNTRY_SLUGS,
)
from app.schemas.country_onboarding import (
    AllCountriesOnboardingResult,
    CountryOnboardingResult,
    OnboardingFinding,
    OnboardingSection,
)
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from psycopg import Connection
from typing import Any


COUNTRY_ONBOARDING_THRESHOLDS: dict[str, Any] = {
    "required_cii_metrics": 6,
    "required_scenario_scores": 5,
    "minimum_sources": 10,
    "minimum_evidence_items": 15,
    "minimum_legal_signals": 5,
    "minimum_timeline_events": 5,
    "timeline_events_with_source_ratio": 1.0,
    "country_card_required": True,
    "localization_metadata_required": True,
    "matrix_ready_required": True,
    "home_overview_ready_required": True,
}

_ONBOARDING_CHECK_CODES = [
    "country_onboarding_country_card_exists",
    "country_onboarding_cii_metrics_complete",
    "country_onboarding_scenario_scores_complete",
    "country_onboarding_sources_threshold",
    "country_onboarding_evidence_threshold",
    "country_onboarding_legal_signals_threshold",
    "country_onboarding_timeline_events_threshold",
    "country_onboarding_timeline_events_source_backed",
    "country_onboarding_visual_matrix_ready",
    "country_onboarding_home_overview_ready",
    "country_onboarding_localization_ready",
    "country_onboarding_mvp_ready",
]


def evaluate_country_onboarding(
    connection: Connection[Any], country_slug: str
) -> CountryOnboardingResult:
    sections: dict[str, OnboardingSection] = {}
    findings: list[OnboardingFinding] = []
    mvp_ready = True

    base_row = repository.get_country_base(connection, country_slug)
    if base_row is None or not base_row.get("is_active"):
        sections["base"] = OnboardingSection(
            status="missing",
            severity="critical",
            required=1,
            actual=0,
            missing=1,
            message="Country does not exist or is not active.",
        )
        findings.append(
            OnboardingFinding(
                code="country_onboarding_mvp_ready",
                severity="critical",
                message="Country does not exist or is not active.",
            )
        )
        return CountryOnboardingResult(
            country_slug=country_slug,
            mvp_ready=False,
            sections=sections,
            findings=findings,
        )

    sections["base"] = OnboardingSection(
        status="ready", severity="info", required=1, actual=1, missing=0
    )

    card_count = repository.count_published_country_cards(connection, country_slug)
    if card_count == 0:
        sections["country_card"] = OnboardingSection(
            status="missing",
            severity="critical",
            required=1,
            actual=0,
            missing=1,
            message="Country has no published country card.",
        )
        findings.append(
            OnboardingFinding(
                code="country_onboarding_country_card_exists",
                severity="critical",
                message="Country does not have a published country card.",
            )
        )
        mvp_ready = False
    else:
        sections["country_card"] = OnboardingSection(
            status="ready", severity="info", required=1, actual=card_count, missing=0
        )

    active_metrics = repository.count_active_cii_metrics(connection)
    metric_values = repository.count_country_cii_metric_values(connection, country_slug)
    cii_missing = max(0, active_metrics - metric_values)
    if metric_values < active_metrics:
        sections["cii_metrics"] = OnboardingSection(
            status="missing",
            severity="critical",
            required=active_metrics,
            actual=metric_values,
            missing=cii_missing,
            message="Country is missing active CII metric values.",
        )
        findings.append(
            OnboardingFinding(
                code="country_onboarding_cii_metrics_complete",
                severity="critical",
                message=f"Country has {metric_values}/{active_metrics} active CII metric values.",
            )
        )
        mvp_ready = False
    else:
        sections["cii_metrics"] = OnboardingSection(
            status="ready",
            severity="info",
            required=active_metrics,
            actual=metric_values,
            missing=0,
        )

    required_scenarios = COUNTRY_ONBOARDING_THRESHOLDS["required_scenario_scores"]
    scenario_scores = repository.count_cii_scenario_scores(
        connection, country_slug, MVP_SCENARIO_SLUGS
    )
    scenario_missing = max(0, required_scenarios - scenario_scores)
    if scenario_scores < required_scenarios:
        sections["scenario_scores"] = OnboardingSection(
            status="missing",
            severity="critical",
            required=required_scenarios,
            actual=scenario_scores,
            missing=scenario_missing,
            message="Country does not have all required CII scenario scores.",
        )
        findings.append(
            OnboardingFinding(
                code="country_onboarding_scenario_scores_complete",
                severity="critical",
                message=f"Country has {scenario_scores}/{required_scenarios} required CII scenario scores.",
            )
        )
        mvp_ready = False
    else:
        sections["scenario_scores"] = OnboardingSection(
            status="ready",
            severity="info",
            required=required_scenarios,
            actual=scenario_scores,
            missing=0,
        )

    min_sources = COUNTRY_ONBOARDING_THRESHOLDS["minimum_sources"]
    sources_count = repository.count_published_sources(connection, country_slug)
    sources_missing = max(0, min_sources - sources_count)
    if sources_count < min_sources:
        sections["sources"] = OnboardingSection(
            status="incomplete",
            severity="critical",
            required=min_sources,
            actual=sources_count,
            missing=sources_missing,
            message="Country has too few published sources.",
        )
        findings.append(
            OnboardingFinding(
                code="country_onboarding_sources_threshold",
                severity="critical",
                message=f"Country has {sources_count} published sources; {min_sources} required.",
            )
        )
        mvp_ready = False
    else:
        sections["sources"] = OnboardingSection(
            status="ready",
            severity="info",
            required=min_sources,
            actual=sources_count,
            missing=0,
        )

    min_evidence = COUNTRY_ONBOARDING_THRESHOLDS["minimum_evidence_items"]
    evidence_count = repository.count_published_evidence(connection, country_slug)
    evidence_missing = max(0, min_evidence - evidence_count)
    if evidence_count < min_evidence:
        sections["evidence"] = OnboardingSection(
            status="incomplete",
            severity="critical",
            required=min_evidence,
            actual=evidence_count,
            missing=evidence_missing,
            message="Country has too few published evidence items.",
        )
        findings.append(
            OnboardingFinding(
                code="country_onboarding_evidence_threshold",
                severity="critical",
                message=f"Country has {evidence_count} published evidence items; {min_evidence} required.",
            )
        )
        mvp_ready = False
    else:
        sections["evidence"] = OnboardingSection(
            status="ready",
            severity="info",
            required=min_evidence,
            actual=evidence_count,
            missing=0,
        )

    min_legal = COUNTRY_ONBOARDING_THRESHOLDS["minimum_legal_signals"]
    legal_count = repository.count_published_legal_signals(connection, country_slug)
    legal_missing = max(0, min_legal - legal_count)
    if legal_count < min_legal:
        sections["legal_signals"] = OnboardingSection(
            status="missing",
            severity="critical",
            required=min_legal,
            actual=legal_count,
            missing=legal_missing,
            message="Country has too few published legal signals.",
        )
        findings.append(
            OnboardingFinding(
                code="country_onboarding_legal_signals_threshold",
                severity="critical",
                message=f"Country has {legal_count} published legal signals; {min_legal} required.",
            )
        )
        mvp_ready = False
    else:
        sections["legal_signals"] = OnboardingSection(
            status="ready",
            severity="info",
            required=min_legal,
            actual=legal_count,
            missing=0,
        )

    min_timeline = COUNTRY_ONBOARDING_THRESHOLDS["minimum_timeline_events"]
    timeline_count = repository.count_timeline_events(connection, country_slug)
    timeline_sourced = repository.count_timeline_events_with_traceability(
        connection, country_slug
    )
    timeline_missing = max(0, min_timeline - timeline_count)
    if timeline_count < min_timeline:
        sections["timeline"] = OnboardingSection(
            status="missing",
            severity="critical",
            required=min_timeline,
            actual=timeline_count,
            missing=timeline_missing,
            message="Country has too few legal signal timeline events.",
        )
        findings.append(
            OnboardingFinding(
                code="country_onboarding_timeline_events_threshold",
                severity="critical",
                message=f"Country has {timeline_count} timeline events; {min_timeline} required.",
            )
        )
        mvp_ready = False
    elif timeline_count > 0 and timeline_sourced < timeline_count:
        unsourced = timeline_count - timeline_sourced
        sections["timeline"] = OnboardingSection(
            status="incomplete",
            severity="critical",
            required=timeline_count,
            actual=timeline_sourced,
            missing=unsourced,
            message="Not all timeline events have source or evidence traceability.",
        )
        findings.append(
            OnboardingFinding(
                code="country_onboarding_timeline_events_source_backed",
                severity="critical",
                message=f"{unsourced} timeline event(s) lack source or evidence traceability.",
            )
        )
        mvp_ready = False
    else:
        sections["timeline"] = OnboardingSection(
            status="ready",
            severity="info",
            required=min_timeline,
            actual=timeline_count,
            missing=0,
        )

    matrix_ready = scenario_scores >= required_scenarios
    if not matrix_ready:
        sections["matrix"] = OnboardingSection(
            status="blocked",
            severity="critical",
            required=required_scenarios,
            actual=scenario_scores,
            missing=scenario_missing,
            message="Country cannot participate in the compare matrix without all scenario CII scores.",
        )
        findings.append(
            OnboardingFinding(
                code="country_onboarding_visual_matrix_ready",
                severity="critical",
                message="Country is not ready for the compare matrix view.",
            )
        )
        mvp_ready = False
    else:
        sections["matrix"] = OnboardingSection(
            status="ready",
            severity="info",
            required=required_scenarios,
            actual=scenario_scores,
            missing=0,
        )

    home_ready = scenario_scores >= 1 and timeline_count >= 1 and card_count >= 1
    if not home_ready:
        sections["home_overview"] = OnboardingSection(
            status="blocked",
            severity="critical",
            required=1,
            actual=0,
            missing=1,
            message="Country is not ready for the home overview.",
        )
        findings.append(
            OnboardingFinding(
                code="country_onboarding_home_overview_ready",
                severity="critical",
                message="Country needs CII score, timeline events, and country card for the home overview.",
            )
        )
        mvp_ready = False
    else:
        sections["home_overview"] = OnboardingSection(
            status="ready", severity="info", required=1, actual=1, missing=0
        )

    has_localization = repository.check_localization_metadata(connection, country_slug)
    if not has_localization:
        sections["localization"] = OnboardingSection(
            status="missing",
            severity="critical",
            required=1,
            actual=0,
            missing=1,
            message="Country is missing required localization metadata (name, iso2).",
        )
        findings.append(
            OnboardingFinding(
                code="country_onboarding_localization_ready",
                severity="critical",
                message="Country does not have required localization metadata.",
            )
        )
        mvp_ready = False
    else:
        sections["localization"] = OnboardingSection(
            status="ready", severity="info", required=1, actual=1, missing=0
        )

    return CountryOnboardingResult(
        country_slug=country_slug,
        mvp_ready=mvp_ready,
        sections=sections,
        findings=findings,
    )


def evaluate_all_mvp_countries(
    connection: Connection[Any],
) -> AllCountriesOnboardingResult:
    mvp_results = [
        evaluate_country_onboarding(connection, slug) for slug in MVP_COUNTRY_SLUGS
    ]
    onboarding_results = [
        evaluate_country_onboarding(connection, slug)
        for slug in ONBOARDING_COUNTRY_SLUGS
    ]
    return AllCountriesOnboardingResult(
        countries=mvp_results,
        onboarding_countries=onboarding_results,
        all_mvp_ready=all(r.mvp_ready for r in mvp_results),
    )


def build_country_onboarding_dq_results(
    connection: Connection[Any],
) -> tuple[list[DataQualityCheck], list[DataQualityIssue]]:
    checks: list[DataQualityCheck] = []
    issues: list[DataQualityIssue] = []

    all_results = evaluate_all_mvp_countries(connection)

    for result in all_results.countries:
        for finding in result.findings:
            issues.append(
                DataQualityIssue(
                    code=finding.code,
                    severity=finding.severity,
                    entity_type="country",
                    entity_id=result.country_slug,
                    message=f"[{result.country_slug}] {finding.message}",
                    details={
                        "country_slug": result.country_slug,
                        "section": _finding_code_to_section(finding.code),
                    },
                )
            )

    for check_code in _ONBOARDING_CHECK_CODES:
        failed = any(i.code == check_code for i in issues)
        checks.append(
            DataQualityCheck(code=check_code, status="failed" if failed else "passed")
        )

    for result in all_results.onboarding_countries:
        for finding in result.findings:
            issues.append(
                DataQualityIssue(
                    code=f"onboarding_{finding.code}",
                    severity="warning",
                    entity_type="country",
                    entity_id=result.country_slug,
                    message=f"[onboarding:{result.country_slug}] {finding.message}",
                    details={
                        "country_slug": result.country_slug,
                        "section": _finding_code_to_section(finding.code),
                        "onboarding": True,
                    },
                )
            )

    return checks, issues


def _finding_code_to_section(code: str) -> str:
    mapping = {
        "country_onboarding_country_card_exists": "country_card",
        "country_onboarding_cii_metrics_complete": "cii_metrics",
        "country_onboarding_scenario_scores_complete": "scenario_scores",
        "country_onboarding_sources_threshold": "sources",
        "country_onboarding_evidence_threshold": "evidence",
        "country_onboarding_legal_signals_threshold": "legal_signals",
        "country_onboarding_timeline_events_threshold": "timeline",
        "country_onboarding_timeline_events_source_backed": "timeline",
        "country_onboarding_visual_matrix_ready": "matrix",
        "country_onboarding_home_overview_ready": "home_overview",
        "country_onboarding_localization_ready": "localization",
        "country_onboarding_mvp_ready": "base",
    }
    return mapping.get(code, code)
