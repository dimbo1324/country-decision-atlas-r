from app.core.database import get_connection
from app.core.locales import LocaleQuery
from app.repositories.common import build_locale
from app.repositories.legal_signals import count_legal_signals, list_legal_signals
from app.schemas.common import Pagination, SortMeta
from app.schemas.decision_engine import (
    EvidenceListResponse,
    LegalSignalDetailListResponse,
    LegalSignalDetailResponse,
)
from app.schemas.legal_signals import LegalSignalListResponse
from app.services import decision_engine
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any, Literal


router = APIRouter(
    prefix="/countries/{country_id}/legal-signals", tags=["legal_signals"]
)


@router.get("", response_model=LegalSignalListResponse)
async def read_country_legal_signals(
    country_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    signal_type: str | None = None,
    impact_direction: str | None = None,
    impact_level: str | None = None,
    status: Literal["published", "archived"] = "published",
    sort: Literal[
        "published_date", "effective_date", "impact_level", "created_at", "updated_at"
    ] = "published_date",
    order: Literal["asc", "desc"] = "desc",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> LegalSignalListResponse:
    rows = list_legal_signals(
        connection,
        country_id,
        locale,
        limit,
        offset,
        signal_type,
        impact_direction,
        impact_level,
        status,
        sort,
        order,
    )
    total = count_legal_signals(
        connection, country_id, signal_type, impact_direction, impact_level, status
    )
    return LegalSignalListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        sort=SortMeta(sort=sort, order=order),
        locale=build_locale(rows, locale),
    )


top_level_router = APIRouter(prefix="/legal-signals", tags=["legal_signals"])


@top_level_router.get("", response_model=LegalSignalDetailListResponse)
async def read_legal_signals(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    country_slug: str | None = None,
    signal_type: str | None = None,
    impact_direction: str | None = None,
    impact_level: str | None = None,
    status: Literal["published", "archived"] = "published",
    sort: Literal[
        "published_date", "effective_date", "impact_level", "created_at", "updated_at"
    ] = "published_date",
    order: Literal["asc", "desc"] = "desc",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> LegalSignalDetailListResponse:
    rows, pagination, locale_meta, sort_meta = decision_engine.list_legal_signals(
        connection,
        locale,
        country_slug,
        limit,
        offset,
        signal_type,
        impact_direction,
        impact_level,
        status,
        sort,
        order,
    )
    return LegalSignalDetailListResponse(
        items=rows, pagination=pagination, sort=sort_meta, locale=locale_meta
    )


@top_level_router.get("/{signal_id}", response_model=LegalSignalDetailResponse)
async def read_legal_signal(
    signal_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> LegalSignalDetailResponse:
    return decision_engine.get_legal_signal(connection, signal_id, locale)


@top_level_router.get("/{signal_id}/evidence", response_model=EvidenceListResponse)
async def read_legal_signal_evidence(
    signal_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> EvidenceListResponse:
    return decision_engine.get_legal_signal_evidence(connection, signal_id)
