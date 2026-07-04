from app.schemas.data_quality import (
    DataQualityCheck,
    DataQualityIssue,
    DataQualityReport,
)
from app.services.data_quality.ai_checks import _append_ai_foundation_checks
from app.services.data_quality.auth_checks import _append_auth_watchlist_checks
from app.services.data_quality.cii_checks import _append_cii_checks
from app.services.data_quality.content_checks import _append_content_checks
from app.services.data_quality.country_drift_checks import (
    _append_country_drift_checks,
)
from app.services.data_quality.country_pair_checks import (
    _append_country_pair_checks,
)
from app.services.data_quality.decision_passport_checks import (
    _append_decision_passport_checks,
)
from app.services.data_quality.decision_personalization_checks import (
    _append_decision_personalization_checks,
)
from app.services.data_quality.migration_board_checks import (
    _append_migration_board_checks,
)
from app.services.data_quality.mvp_checks import _append_mvp_checks
from app.services.data_quality.persona_checks import (
    _append_persona_layer_checks,
)
from app.services.data_quality.platform_checks import (
    _append_platform_runtime_checks,
)
from app.services.data_quality.publication_checks import (
    _append_publication_checks,
)
from app.services.data_quality.route_checklist_checks import (
    _append_route_checklist_checks,
)
from app.services.data_quality.route_checks import _append_route_checks
from app.services.data_quality.search_foundation_checks import (
    _append_search_foundation_checks,
)
from app.services.data_quality.timeline_checks import _append_timeline_checks
from app.services.data_quality.trust_checks import _append_trust_surface_checks
from app.services.data_quality.what_changed_checks import (
    _append_what_changed_checks,
)
from psycopg import Connection
from typing import Any


def build_data_quality_report(connection: Connection[Any]) -> DataQualityReport:
    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []

    _append_mvp_checks(connection, issues, checks)
    _append_content_checks(connection, issues, checks)
    _append_publication_checks(connection, issues, checks)
    _append_timeline_checks(connection, issues, checks)
    _append_cii_checks(connection, issues, checks)
    _append_route_checks(connection, issues, checks)
    _append_persona_layer_checks(connection, issues, checks)
    _append_platform_runtime_checks(connection, issues, checks)
    _append_trust_surface_checks(connection, issues, checks)
    _append_country_drift_checks(connection, issues, checks)
    _append_decision_personalization_checks(connection, issues, checks)
    _append_decision_passport_checks(connection, issues, checks)
    _append_country_pair_checks(connection, issues, checks)
    _append_route_checklist_checks(connection, issues, checks)
    _append_what_changed_checks(connection, issues, checks)
    _append_search_foundation_checks(connection, issues, checks)
    _append_ai_foundation_checks(connection, issues, checks)
    _append_auth_watchlist_checks(connection, issues, checks)
    _append_migration_board_checks(connection, issues, checks)

    from app.services import data_quality as data_quality_facade

    translation_checks, translation_issues = (
        data_quality_facade.build_translation_quality_results(connection)
    )
    checks.extend(translation_checks)
    issues.extend(translation_issues)
    onboarding_checks, onboarding_issues = (
        data_quality_facade.build_country_onboarding_dq_results(connection)
    )
    checks.extend(onboarding_checks)
    issues.extend(onboarding_issues)
    critical_issues_count = sum(
        1 for issue in issues if issue.severity == "critical"
    )
    warnings_count = sum(
        1
        for issue in issues
        if issue.severity in {"warning", "accepted_mvp_warning"}
    )
    return DataQualityReport(
        overall_status="valid" if critical_issues_count == 0 else "invalid",
        valid=critical_issues_count == 0,
        critical_issues_count=critical_issues_count,
        warnings_count=warnings_count,
        checks=checks,
        issues=issues,
    )
