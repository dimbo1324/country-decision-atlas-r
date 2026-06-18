from app.core.database import get_connection
from app.core.locales import LocaleQuery
from app.repositories.sources import (
    count_evidence_items,
    count_sources,
    list_evidence_items,
    list_sources,
)
from app.schemas.common import Pagination, SortMeta, source_locale_resolution
from app.schemas.sources import (
    EvidenceItemListResponse,
    SourceListResponse,
    SourceResponse,
)
from app.services import decision_engine
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any, Literal


router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=SourceListResponse)
async def read_sources(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    country_slug: str | None = None,
    source_type: str | None = None,
    language: str | None = None,
    confidence: Literal["low", "medium", "high"] | None = None,
    status: Literal["published", "archived"] = "published",
    sort: Literal[
        "title", "created_at", "published_at", "last_checked_at", "confidence"
    ] = "last_checked_at",
    order: Literal["asc", "desc"] = "desc",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SourceListResponse:
    rows = list_sources(
        connection,
        limit,
        offset,
        country_slug,
        source_type,
        language,
        confidence,
        status,
        sort,
        order,
    )
    total = count_sources(
        connection, country_slug, source_type, language, confidence, status
    )
    return SourceListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        sort=SortMeta(sort=sort, order=order),
        locale=source_locale_resolution(locale),
    )


@router.get("/evidence-items", response_model=EvidenceItemListResponse)
async def read_evidence_items(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    country_slug: str | None = None,
    source_id: str | None = None,
    legal_signal_id: str | None = None,
    confidence: Literal["low", "medium", "high"] | None = None,
    status: Literal["published", "archived"] = "published",
    sort: Literal["retrieved_at", "created_at", "confidence"] = "retrieved_at",
    order: Literal["asc", "desc"] = "desc",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> EvidenceItemListResponse:
    rows = list_evidence_items(
        connection,
        limit,
        offset,
        country_slug,
        source_id,
        legal_signal_id,
        confidence,
        status,
        sort,
        order,
    )
    total = count_evidence_items(
        connection, country_slug, source_id, legal_signal_id, confidence, status
    )
    return EvidenceItemListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        sort=SortMeta(sort=sort, order=order),
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
