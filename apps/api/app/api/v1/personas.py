from app.core.database import get_connection
from app.core.errors import api_error
from app.core.locales import LocaleQuery
from app.repositories import personas as personas_repository
from app.repositories.common import build_locale
from app.schemas.personas import (
    Persona,
    PersonaListResponse,
    PersonaWeightProfile,
    PersonaWeightProfileResponse,
)
from app.services.persona_weights import build_persona_weight_profile
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("", response_model=PersonaListResponse)
def read_personas(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> PersonaListResponse:
    rows = personas_repository.list_personas(connection, locale)
    return PersonaListResponse(items=rows, locale=build_locale(rows, locale))


@router.get("/{persona_slug}", response_model=Persona)
def read_persona(
    persona_slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> Persona:
    row = personas_repository.get_persona_by_slug(
        connection, persona_slug, locale
    )
    if row is None:
        raise api_error(
            404,
            "persona_not_found",
            "Persona not found.",
            {"persona_slug": persona_slug},
        )
    return Persona.model_validate(row)


@router.get(
    "/{persona_slug}/weights", response_model=PersonaWeightProfileResponse
)
def read_persona_weights(
    persona_slug: str,
    scenario: Annotated[str, Query(description="Scenario slug")],
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    version: str = Query("v1.0", pattern=r"^v\d+\.\d+$"),
) -> PersonaWeightProfileResponse:
    profile = build_persona_weight_profile(
        connection,
        scenario,
        persona_slug,
        locale,
        version,
    )
    return PersonaWeightProfileResponse(
        item=PersonaWeightProfile.model_validate(profile)
    )
