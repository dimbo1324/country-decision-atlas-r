from app.core.database import get_connection
from app.core.locales import LocaleQuery
from app.repositories.common import build_locale
from app.repositories.legal_signals import count_legal_signals, list_legal_signals
from app.schemas.common import Pagination
from app.schemas.decision_engine import (
    EvidenceListResponse,
    LegalSignalDetailListResponse,
    LegalSignalDetailResponse,
)
from app.schemas.legal_signals import LegalSignalListResponse
from app.services import decision_engine
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(
    prefix="/countries/{country_id}/legal-signals", tags=["legal_signals"]
)


@router.get("", response_model=LegalSignalListResponse)
async def read_country_legal_signals(
    country_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> LegalSignalListResponse:
    rows = list_legal_signals(connection, country_id, locale, limit, offset)
    total = count_legal_signals(connection, country_id)
    return LegalSignalListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        locale=build_locale(rows, locale),
    )


top_level_router = APIRouter(prefix="/legal-signals", tags=["legal_signals"])


@top_level_router.get("", response_model=LegalSignalDetailListResponse)
async def read_legal_signals(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    country_slug: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> LegalSignalDetailListResponse:
    rows, pagination, locale_meta = decision_engine.list_legal_signals(
        connection, locale, country_slug, limit, offset
    )
    return LegalSignalDetailListResponse(
        items=rows, pagination=pagination, locale=locale_meta
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
