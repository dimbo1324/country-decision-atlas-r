from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.errors import api_error
from app.core.rbac import require_admin
from app.repositories import country_drift as country_drift_repo
from app.schemas.common import ErrorResponse
from app.schemas.country_drift import (
    CountryDriftBatchRecomputeResult,
    CountryDriftHistoryItem,
    CountryDriftRecomputeRequest,
    CountryDriftRecomputeResult,
    CountryDriftResponse,
    CountryDriftSnapshot,
)
from app.services.country_drift import (
    compute_and_store_all_country_drifts,
    compute_and_store_country_drift,
)
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(tags=["country-drift"])
admin_router = APIRouter(tags=["admin"])

_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorResponse},
    404: {"description": "Not found"},
}


def _optional_float(value: Any) -> float | None:
    return float(value) if value is not None else None


def _build_snapshot(row: dict[str, Any]) -> CountryDriftSnapshot:
    return CountryDriftSnapshot(
        country_slug=row["country_slug"],
        period_start=row["period_start"],
        period_end=row["period_end"],
        window_days=row["window_days"],
        label=row["label"],
        previous_label=row.get("previous_label"),
        confidence=row["confidence"],
        net_score=_optional_float(row.get("net_score")),
        positive_weight=float(row["positive_weight"]),
        negative_weight=float(row["negative_weight"]),
        neutral_weight=float(row["neutral_weight"]),
        mixed_weight=float(row["mixed_weight"]),
        uncertain_weight=float(row["uncertain_weight"]),
        total_weight=float(row["total_weight"]),
        event_count=row["event_count"],
        positive_count=row["positive_count"],
        negative_count=row["negative_count"],
        neutral_count=row["neutral_count"],
        mixed_count=row["mixed_count"],
        uncertain_count=row["uncertain_count"],
        methodology_version=row["methodology_version"],
        input_summary=row.get("input_summary") or {},
        computed_at=row["computed_at"],
        expires_at=row.get("expires_at"),
    )


def _build_history_item(row: dict[str, Any]) -> CountryDriftHistoryItem:
    return CountryDriftHistoryItem(
        period_start=row["period_start"],
        period_end=row["period_end"],
        label=row["label"],
        confidence=row["confidence"],
        net_score=_optional_float(row.get("net_score")),
        event_count=row["event_count"],
        computed_at=row["computed_at"],
    )


@router.get(
    "/countries/{country_slug}/drift",
    response_model=CountryDriftResponse,
    responses=_RESPONSES,
)
def get_country_drift(
    country_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    limit: int = Query(12, ge=1, le=50),
    locale: str | None = Query(None),  # noqa: ARG001
) -> CountryDriftResponse:
    country = country_drift_repo.get_country_for_drift(connection, country_slug)
    if country is None or country.get("is_demo"):
        raise api_error(
            404,
            "country_drift_country_not_found",
            f"Country not found: {country_slug}",
        )
    latest_row = country_drift_repo.get_latest_drift_snapshot(
        connection, country_slug
    )
    history_rows = country_drift_repo.list_drift_snapshots(
        connection, country_slug, limit=limit
    )
    return CountryDriftResponse(
        country_slug=country_slug,
        latest_snapshot=_build_snapshot(latest_row) if latest_row else None,
        history=[_build_history_item(row) for row in history_rows],
    )


@admin_router.post(
    "/admin/country-drift/recompute",
    response_model=CountryDriftBatchRecomputeResult,
    responses={401: {"model": ErrorResponse}},
)
def admin_recompute_all_country_drift(
    payload: CountryDriftRecomputeRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_admin)],
) -> CountryDriftBatchRecomputeResult:
    result = compute_and_store_all_country_drifts(
        connection, dry_run=payload.dry_run, emit_events=payload.emit_events
    )
    if not payload.dry_run:
        connection.commit()
    return CountryDriftBatchRecomputeResult(
        countries_processed=result.countries_processed,
        snapshots_written=result.snapshots_written,
        events_emitted=result.events_emitted,
        insufficient_data_count=result.insufficient_data_count,
        errors=result.errors,
    )


@admin_router.post(
    "/admin/country-drift/recompute/{country_slug}",
    response_model=CountryDriftRecomputeResult,
    responses={401: {"model": ErrorResponse}},
)
def admin_recompute_country_drift(
    country_slug: str,
    payload: CountryDriftRecomputeRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_admin)],
) -> CountryDriftRecomputeResult:
    result = compute_and_store_country_drift(
        connection,
        country_slug=country_slug,
        dry_run=payload.dry_run,
        emit_events=payload.emit_events,
    )
    if not payload.dry_run and result.stored:
        connection.commit()
    return CountryDriftRecomputeResult(
        country_slug=result.country_slug,
        country_not_found=result.country_not_found,
        dry_run=result.dry_run,
        computed=result.computed,
        stored=result.stored,
        label=result.label,
        previous_label=result.previous_label,
        confidence=result.confidence,
        net_score=_optional_float(result.net_score),
        event_count=result.event_count,
        event_emitted=result.event_emitted,
        error=result.error,
    )
