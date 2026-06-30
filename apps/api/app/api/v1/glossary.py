from app.core.database import get_connection
from app.core.errors import api_error
from app.repositories import glossary as glossary_repo
from app.schemas.glossary import GlossaryListResponse, GlossaryTerm
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(tags=["glossary"])

_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {"description": "Not found"},
}


@router.get(
    "/glossary",
    response_model=GlossaryListResponse,
)
def list_glossary_terms(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: str | None = Query(None),
    category: str | None = Query(None),
    q: str | None = Query(None),
) -> GlossaryListResponse:
    effective_locale = locale if locale in ("en", "ru") else "en"
    rows = glossary_repo.list_glossary_terms(connection, effective_locale, category, q)
    return GlossaryListResponse(items=[_build_term(r) for r in rows])


@router.get(
    "/glossary/{term_slug}",
    response_model=GlossaryTerm,
    responses=_RESPONSES,
)
def get_glossary_term(
    term_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: str | None = Query(None),
) -> GlossaryTerm:
    effective_locale = locale if locale in ("en", "ru") else "en"
    row = glossary_repo.get_glossary_term(connection, term_slug, effective_locale)
    if row is None:
        raise api_error(
            404, "glossary_not_found", f"Glossary term not found: {term_slug}"
        )
    return _build_term(row)


def _build_term(row: dict[str, Any]) -> GlossaryTerm:
    related = row.get("related_terms") or []
    if isinstance(related, str):
        import json

        related = json.loads(related)
    return GlossaryTerm(
        slug=row["slug"],
        term=row["term"],
        definition=row["definition"],
        category=row["category"],
        related_terms=list(related),
        display_order=row.get("display_order", 0),
        updated_at=row.get("updated_at"),
    )
