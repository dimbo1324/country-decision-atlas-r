from app.core.auth import CurrentUser
from app.core.database import get_connection
from app.core.errors import api_error
from app.core.rbac import require_admin
from app.repositories import trust as trust_repo
from app.schemas.common import ErrorResponse
from app.schemas.trust import (
    CountryTrustResponse,
    TrustComponentBreakdown,
    TrustRecomputeCountryResult,
    TrustRecomputeRequest,
    TrustRecomputeSummary,
)
from app.services.trust_runtime import (
    compute_and_store_trust_for_all_countries,
    compute_and_store_trust_for_country,
)
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(tags=["trust"])
admin_router = APIRouter(tags=["admin"])

_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorResponse},
    404: {"description": "Not found"},
}


def _build_trust_response(row: dict[str, Any]) -> CountryTrustResponse:
    raw = row.get("input_summary") or {}
    components_raw = raw.get("components", {}) if isinstance(raw, dict) else {}
    components = TrustComponentBreakdown(
        source_quality_score=components_raw.get("source_quality_score"),
        evidence_depth_score=components_raw.get("evidence_depth_score"),
        freshness_score=components_raw.get("freshness_score"),
        review_coverage_score=components_raw.get("review_coverage_score"),
        contradiction_component=components_raw.get("contradiction_component"),
    )
    return CountryTrustResponse(
        country_slug=row["country_slug"],
        trust_score=float(row["trust_score"])
        if row.get("trust_score") is not None
        else None,
        trust_label=row["trust_label"],
        confidence=row["confidence"],
        freshness_status=row["freshness_status"],
        source_count=row.get("source_count", 0),
        evidence_count=row.get("evidence_count", 0),
        legal_signal_count=row.get("legal_signal_count", 0),
        route_count=row.get("route_count", 0),
        platform_metric_count=row.get("platform_metric_count", 0),
        contradiction_score=float(row["contradiction_score"])
        if row.get("contradiction_score") is not None
        else None,
        components=components,
        last_verified_at=row.get("last_verified_at"),
        computed_at=row.get("computed_at"),
        expires_at=row.get("expires_at"),
        methodology_version=row.get("methodology_version", "v1.0"),
    )


@router.get(
    "/countries/{country_slug}/trust",
    response_model=CountryTrustResponse,
    responses=_RESPONSES,
)
def get_country_trust(
    country_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: str | None = Query(None),  # noqa: ARG001
) -> CountryTrustResponse:
    row = trust_repo.get_country_trust_score(connection, country_slug)
    if row is None:
        raise api_error(
            404, "trust_not_found", f"Trust score not found for country: {country_slug}"
        )
    return _build_trust_response(row)


@admin_router.post(
    "/admin/trust/recompute",
    response_model=TrustRecomputeSummary,
    responses={401: {"model": ErrorResponse}},
)
def admin_recompute_all_trust(
    payload: TrustRecomputeRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_admin)],
) -> TrustRecomputeSummary:
    result = compute_and_store_trust_for_all_countries(
        connection, dry_run=payload.dry_run
    )
    if not payload.dry_run:
        connection.commit()
    return TrustRecomputeSummary(**result)


@admin_router.post(
    "/admin/trust/recompute/{country_slug}",
    response_model=TrustRecomputeCountryResult,
    responses={401: {"model": ErrorResponse}},
)
def admin_recompute_country_trust(
    country_slug: str,
    payload: TrustRecomputeRequest,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    _: Annotated[CurrentUser, Depends(require_admin)],
) -> TrustRecomputeCountryResult:
    result = compute_and_store_trust_for_country(
        connection, country_slug, dry_run=payload.dry_run
    )
    if not payload.dry_run and result.get("stored"):
        connection.commit()
    return TrustRecomputeCountryResult(**result)
