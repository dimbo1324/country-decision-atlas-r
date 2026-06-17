from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from psycopg import Connection

from app.core.database import get_connection
from app.repositories.sources import (
    count_evidence_items,
    count_sources,
    list_evidence_items,
    list_sources,
)
from app.schemas.common import Pagination
from app.schemas.sources import EvidenceItemListResponse, SourceListResponse

router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=SourceListResponse)
async def read_sources(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SourceListResponse:
    rows = list_sources(connection, limit, offset)
    total = count_sources(connection)
    return SourceListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
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
