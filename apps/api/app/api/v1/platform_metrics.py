from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.errors import api_error
from app.core.rbac import require_admin
from app.repositories import platform_metrics as pm_repo
from app.schemas.common import ErrorResponse
from app.schemas.platform_metrics import (
    PlatformMetric,
    PlatformMetricDetailResponse,
    PlatformMetricInputSummary,
    PlatformMetricListResponse,
    PlatformMetricsRecomputeRequest,
    PlatformMetricsRecomputeResult,
    PlatformMetricsRecomputeSummary,
)
from app.services.platform_metrics_runtime import (
    VALID_METRIC_KEYS,
    compute_platform_metrics_for_all_countries,
    compute_platform_metrics_for_country,
    is_feature_enabled,
)
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(tags=["platform-metrics"])

PLATFORM_METRICS_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorResponse},
    404: {"description": "Not found"},
    422: {"description": "Unprocessable Entity"},
}


def _build_metric(
    row: dict[str, Any], include_input_summary: bool
) -> PlatformMetric:
    raw_scenario = row.get("scenario_slug")
    scenario_slug = (
        None
        if raw_scenario is None or raw_scenario == pm_repo.GLOBAL_SCENARIO_SLUG
        else str(raw_scenario)
    )
    input_summary: PlatformMetricInputSummary | None = None
    if include_input_summary:
        raw_summary = row.get("input_summary") or {}
        input_summary = PlatformMetricInputSummary(
            raw=raw_summary if isinstance(raw_summary, dict) else {}
        )
    return PlatformMetric(
        country_slug=str(row["country_slug"]),
        metric_key=str(row["metric_key"]),
        scenario_slug=scenario_slug,
        value=float(row["value"]) if row.get("value") is not None else None,
        label=str(row["label"]),
        confidence=str(row["confidence"]),
        freshness_status=str(row["freshness_status"]),
        window_days=int(row["window_days"]),
        methodology_version=str(row["methodology_version"]),
        input_summary=input_summary,
        source_count=int(row.get("source_count") or 0),
        evidence_count=int(row.get("evidence_count") or 0),
        signal_count=int(row.get("signal_count") or 0),
        event_count=int(row.get("event_count") or 0),
        computed_at=row.get("computed_at"),
        expires_at=row.get("expires_at"),
    )


@router.get(
    "/countries/{country_slug}/platform-metrics",
    response_model=PlatformMetricListResponse,
    responses=PLATFORM_METRICS_RESPONSES,
)
def list_country_platform_metrics(
    country_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    scenario: str | None = Query(None),
    locale: str | None = Query(None),  # noqa: ARG001
    include_input_summary: bool = Query(True),
) -> PlatformMetricListResponse:
    if not is_feature_enabled(connection):
        raise api_error(
            403,
            "self_computed_intelligence_disabled",
            "Self-computed intelligence feature is disabled.",
        )
    country = pm_repo.get_country_by_slug(connection, country_slug)
    if country is None or country.get("is_demo"):
        raise api_error(
            404,
            "country_not_found",
            "Country not found.",
            {"country_slug": country_slug},
        )
    if scenario is not None and scenario not in [
        "relocation_residence",
        "permanent_residence_citizenship",
        "low_budget_living",
        "business_self_employment",
        "safety_political_risk",
    ]:
        raise api_error(
            422,
            "platform_metric_invalid_scenario",
            "Unknown scenario slug.",
            {"scenario": scenario},
        )
    rows = pm_repo.list_country_platform_metrics(connection, country_slug)
    if scenario is not None:
        rows = [
            r
            for r in rows
            if r.get("scenario_slug") == scenario
            or r.get("scenario_slug") == pm_repo.GLOBAL_SCENARIO_SLUG
        ]
    items = [_build_metric(row, include_input_summary) for row in rows]
    return PlatformMetricListResponse(items=items, country_slug=country_slug)


@router.get(
    "/countries/{country_slug}/platform-metrics/{metric_key}",
    response_model=PlatformMetricDetailResponse,
    responses=PLATFORM_METRICS_RESPONSES,
)
def get_country_platform_metric(
    country_slug: str,
    metric_key: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    scenario: str | None = Query(None),
    locale: str | None = Query(None),  # noqa: ARG001
    include_input_summary: bool = Query(True),
) -> PlatformMetricDetailResponse:
    if not is_feature_enabled(connection):
        raise api_error(
            403,
            "self_computed_intelligence_disabled",
            "Self-computed intelligence feature is disabled.",
        )
    country = pm_repo.get_country_by_slug(connection, country_slug)
    if country is None or country.get("is_demo"):
        raise api_error(
            404,
            "country_not_found",
            "Country not found.",
            {"country_slug": country_slug},
        )
    if metric_key not in VALID_METRIC_KEYS:
        raise api_error(
            422,
            "platform_metric_invalid_key",
            "Unknown metric key.",
            {"metric_key": metric_key},
        )
    if scenario is not None and scenario not in [
        "relocation_residence",
        "permanent_residence_citizenship",
        "low_budget_living",
        "business_self_employment",
        "safety_political_risk",
    ]:
        raise api_error(
            422,
            "platform_metric_invalid_scenario",
            "Unknown scenario slug.",
            {"scenario": scenario},
        )
    row = pm_repo.get_country_platform_metric(
        connection, country_slug, metric_key, scenario
    )
    if row is None:
        raise api_error(
            404,
            "platform_metric_not_found",
            "Platform metric not found.",
            {"country_slug": country_slug, "metric_key": metric_key},
        )
    return PlatformMetricDetailResponse(
        item=_build_metric(row, include_input_summary)
    )


admin_router = APIRouter(tags=["admin"])


@admin_router.post(
    "/admin/platform-metrics/recompute",
    response_model=PlatformMetricsRecomputeSummary,
    responses=PLATFORM_METRICS_RESPONSES,
)
def admin_recompute_all_platform_metrics(
    payload: PlatformMetricsRecomputeRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_admin)],
) -> PlatformMetricsRecomputeSummary:
    if not is_feature_enabled(connection):
        raise api_error(
            403,
            "self_computed_intelligence_disabled",
            "Self-computed intelligence feature is disabled.",
        )
    result = compute_platform_metrics_for_all_countries(
        connection,
        dry_run=payload.dry_run,
        metric_key=payload.metric_key,
        scenario_slug=payload.scenario_slug,
    )
    if not payload.dry_run:
        connection.commit()
    return result


@admin_router.post(
    "/admin/platform-metrics/recompute/{country_slug}",
    response_model=PlatformMetricsRecomputeResult,
    responses=PLATFORM_METRICS_RESPONSES,
)
def admin_recompute_country_platform_metrics(
    country_slug: str,
    payload: PlatformMetricsRecomputeRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_admin)],
) -> PlatformMetricsRecomputeResult:
    if not is_feature_enabled(connection):
        raise api_error(
            403,
            "self_computed_intelligence_disabled",
            "Self-computed intelligence feature is disabled.",
        )
    country = pm_repo.get_country_by_slug(connection, country_slug)
    if country is None:
        raise api_error(
            404,
            "country_not_found",
            "Country not found.",
            {"country_slug": country_slug},
        )
    if (
        payload.metric_key is not None
        and payload.metric_key not in VALID_METRIC_KEYS
    ):
        raise api_error(
            422,
            "platform_metric_invalid_key",
            "Unknown metric key.",
            {"metric_key": payload.metric_key},
        )
    result = compute_platform_metrics_for_country(
        connection,
        country_slug,
        dry_run=payload.dry_run,
        metric_key=payload.metric_key,
        scenario_slug=payload.scenario_slug,
    )
    if not payload.dry_run:
        connection.commit()
    return result
