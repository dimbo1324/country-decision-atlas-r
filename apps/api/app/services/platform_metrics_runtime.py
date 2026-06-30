from app.repositories import feature_flags as ff_repo, platform_metrics as pm_repo
from app.schemas.platform_metrics import (
    PlatformMetricCountryResult,
    PlatformMetricsRecomputeResult,
    PlatformMetricsRecomputeSummary,
)
from app.services import platform_metrics as pm_service
from app.services.feature_flags import can_access, default_access_context
from app.services.platform_metric_types import METHODOLOGY_VERSION
from psycopg import Connection
from typing import Any


FEATURE_KEY = "self_computed_intelligence"

VALID_METRIC_KEYS = {
    "legal_velocity_index",
    "scenario_specific_risk_score",
    "contradiction_score",
}

MVP_SCENARIO_SLUGS = [
    "relocation_residence",
    "permanent_residence_citizenship",
    "low_budget_living",
    "business_self_employment",
    "safety_political_risk",
]


def is_feature_enabled(connection: Connection[Any]) -> bool:
    feature = ff_repo.get_feature_flag(connection, FEATURE_KEY)
    rules = ff_repo.list_feature_access_rules(connection, FEATURE_KEY)
    from app.core.config import get_settings

    ctx = default_access_context(get_settings())
    decision = can_access(ctx, feature, rules, FEATURE_KEY)
    return decision.is_enabled


def compute_platform_metrics_for_country(
    connection: Connection[Any],
    country_slug: str,
    dry_run: bool = False,
    metric_key: str | None = None,
    scenario_slug: str | None = None,
    window_days: int = 365,
    methodology_version: str = METHODOLOGY_VERSION,
) -> PlatformMetricsRecomputeResult:
    feature_enabled = is_feature_enabled(connection)
    if not feature_enabled:
        return PlatformMetricsRecomputeResult(
            feature_enabled=False,
            dry_run=dry_run,
            country_slug=country_slug,
            metrics_computed=0,
            metrics_written=0,
            metrics_failed=0,
            errors=["self_computed_intelligence_disabled"],
        )

    if metric_key is not None and metric_key not in VALID_METRIC_KEYS:
        return PlatformMetricsRecomputeResult(
            feature_enabled=True,
            dry_run=dry_run,
            country_slug=country_slug,
            metrics_computed=0,
            metrics_written=0,
            metrics_failed=0,
            errors=[f"platform_metric_invalid_key: {metric_key}"],
        )

    if scenario_slug is not None and scenario_slug not in MVP_SCENARIO_SLUGS:
        return PlatformMetricsRecomputeResult(
            feature_enabled=True,
            dry_run=dry_run,
            country_slug=country_slug,
            metrics_computed=0,
            metrics_written=0,
            metrics_failed=0,
            errors=[f"platform_metric_invalid_scenario: {scenario_slug}"],
        )

    country = pm_repo.get_country_by_slug(connection, country_slug)
    if country is None:
        return PlatformMetricsRecomputeResult(
            feature_enabled=True,
            dry_run=dry_run,
            country_slug=country_slug,
            metrics_computed=0,
            metrics_written=0,
            metrics_failed=0,
            errors=["country_not_found"],
        )

    try:
        computations = pm_service.compute_country_platform_metrics(
            connection, country_slug, window_days, methodology_version
        )
    except Exception as exc:
        return PlatformMetricsRecomputeResult(
            feature_enabled=True,
            dry_run=dry_run,
            country_slug=country_slug,
            metrics_computed=0,
            metrics_written=0,
            metrics_failed=1,
            errors=[str(exc)],
        )

    if metric_key is not None:
        computations = [c for c in computations if c.metric_key == metric_key]
    if scenario_slug is not None:
        computations = [
            c
            for c in computations
            if c.scenario_slug == scenario_slug
            or c.scenario_slug == pm_repo.GLOBAL_SCENARIO_SLUG
        ]

    metrics_computed = len(computations)
    metrics_written = 0
    metrics_failed = 0
    errors: list[str] = []

    if not dry_run:
        country_id = str(country["id"])
        for computation in computations:
            try:
                pm_repo.upsert_country_platform_metric(
                    connection,
                    country_id,
                    computation.metric_key,
                    computation.scenario_slug,
                    computation.value,
                    computation.label,
                    computation.confidence,
                    computation.freshness_status,
                    computation.window_days,
                    computation.methodology_version,
                    computation.input_summary,
                    computation.source_count,
                    computation.evidence_count,
                    computation.signal_count,
                    computation.event_count,
                )
                metrics_written += 1
            except Exception as exc:
                metrics_failed += 1
                errors.append(str(exc))

    return PlatformMetricsRecomputeResult(
        feature_enabled=True,
        dry_run=dry_run,
        country_slug=country_slug,
        metrics_computed=metrics_computed,
        metrics_written=metrics_written,
        metrics_failed=metrics_failed,
        errors=errors,
    )


def compute_platform_metrics_for_all_countries(
    connection: Connection[Any],
    dry_run: bool = False,
    metric_key: str | None = None,
    scenario_slug: str | None = None,
    window_days: int = 365,
    methodology_version: str = METHODOLOGY_VERSION,
) -> PlatformMetricsRecomputeSummary:
    feature_enabled = is_feature_enabled(connection)
    if not feature_enabled:
        return PlatformMetricsRecomputeSummary(
            feature_enabled=False,
            dry_run=dry_run,
            countries_requested=0,
            countries_processed=0,
            countries_skipped=0,
            metrics_computed=0,
            metrics_written=0,
            metrics_failed=0,
            errors=["self_computed_intelligence_disabled"],
        )

    countries = pm_repo.list_active_countries(connection)
    countries_requested = len(countries)
    countries_processed = 0
    countries_skipped = 0
    total_computed = 0
    total_written = 0
    total_failed = 0
    all_errors: list[str] = []

    for country in countries:
        slug = str(country["slug"])
        result = compute_platform_metrics_for_country(
            connection,
            slug,
            dry_run=dry_run,
            metric_key=metric_key,
            scenario_slug=scenario_slug,
            window_days=window_days,
            methodology_version=methodology_version,
        )
        if result.errors and result.metrics_computed == 0:
            countries_skipped += 1
            for err in result.errors:
                all_errors.append(f"{slug}: {err}")
        else:
            countries_processed += 1
            total_computed += result.metrics_computed
            total_written += result.metrics_written
            total_failed += result.metrics_failed
            for err in result.errors:
                all_errors.append(f"{slug}: {err}")

    return PlatformMetricsRecomputeSummary(
        feature_enabled=True,
        dry_run=dry_run,
        countries_requested=countries_requested,
        countries_processed=countries_processed,
        countries_skipped=countries_skipped,
        metrics_computed=total_computed,
        metrics_written=total_written,
        metrics_failed=total_failed,
        errors=all_errors,
    )


def compute_one_platform_metric(
    connection: Connection[Any],
    country_slug: str,
    metric_key: str,
    scenario_slug: str | None = None,
    dry_run: bool = False,
    window_days: int = 365,
    methodology_version: str = METHODOLOGY_VERSION,
) -> PlatformMetricCountryResult:
    result = compute_platform_metrics_for_country(
        connection,
        country_slug,
        dry_run=dry_run,
        metric_key=metric_key,
        scenario_slug=scenario_slug,
        window_days=window_days,
        methodology_version=methodology_version,
    )
    return PlatformMetricCountryResult(
        country_slug=country_slug,
        metrics_computed=result.metrics_computed,
        metrics_written=result.metrics_written,
        metrics_failed=result.metrics_failed,
        errors=result.errors,
    )
