from app.core.database import get_connection
from app.core.locales import LocaleQuery
from app.repositories.sources import (
    count_evidence_items,
    count_sources,
    list_evidence_items,
    list_sources,
)
from app.schemas.common import Pagination, source_locale_resolution
from app.schemas.sources import (
    EvidenceItemListResponse,
    SourceListResponse,
    SourceResponse,
)
from app.services import decision_engine
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=SourceListResponse)
async def read_sources(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SourceListResponse:
    rows = list_sources(connection, limit, offset)
    total = count_sources(connection)
    return SourceListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        locale=source_locale_resolution(locale),
    )


@router.get("/evidence-items", response_model=EvidenceItemListResponse)
async def read_evidence_items(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> EvidenceItemListResponse:
    rows = list_evidence_items(connection, limit, offset)
    total = count_evidence_items(connection)
    return EvidenceItemListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
    )


@router.get("/sources/{source_id}", response_model=SourceResponse)
async def read_source(
    source_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> SourceResponse:
    return SourceResponse(
        item=decision_engine.get_source(connection, source_id),
        locale=source_locale_resolution(locale),
    )


@router.get("/sources/{source_id}/evidence", response_model=EvidenceItemListResponse)
async def read_source_evidence(
    source_id: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> EvidenceItemListResponse:
    return decision_engine.get_source_evidence(connection, source_id, limit, offset)
