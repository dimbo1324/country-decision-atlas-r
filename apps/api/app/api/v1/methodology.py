from app.core.database import get_connection
from app.core.errors import api_error
from app.repositories import methodology as methodology_repo
from app.schemas.methodology import MethodologyListResponse, MethodologySection
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(tags=["methodology"])

_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {"description": "Not found"},
}


@router.get(
    "/methodology",
    response_model=MethodologyListResponse,
)
def list_methodology_sections(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: str | None = Query(None),
) -> MethodologyListResponse:
    effective_locale = locale if locale in ("en", "ru") else "en"
    rows = methodology_repo.list_methodology_sections(connection, effective_locale)
    return MethodologyListResponse(items=[MethodologySection(**r) for r in rows])


@router.get(
    "/methodology/{section_slug}",
    response_model=MethodologySection,
    responses=_RESPONSES,
)
def get_methodology_section(
    section_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: str | None = Query(None),
) -> MethodologySection:
    effective_locale = locale if locale in ("en", "ru") else "en"
    row = methodology_repo.get_methodology_section(
        connection, section_slug, effective_locale
    )
    if row is None:
        raise api_error(
            404,
            "methodology_not_found",
            f"Methodology section not found: {section_slug}",
        )
    return MethodologySection(**row)
