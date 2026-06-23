from app.core.database import get_connection
from app.core.locales import LocaleQuery
from app.repositories.common import build_locale
from app.repositories.scenarios import count_scenarios, list_scenarios
from app.repositories.scores import run_scenario
from app.schemas.common import Pagination
from app.schemas.countries import ScenarioRunInput, ScenarioRunResult
from app.schemas.decision_engine import (
    DecisionCountryScoreListResponse,
    DecisionScenario,
    DecisionScenarioResponse,
)
from app.schemas.scenarios import ScenarioListResponse
from app.services import decision_engine
from fastapi import APIRouter, Depends, Query
from psycopg import Connection
from typing import Annotated, Any


router = APIRouter(tags=["scenarios"])


@router.get("/scenarios", response_model=ScenarioListResponse)
def read_scenarios(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ScenarioListResponse:
    rows = list_scenarios(connection, locale, limit, offset)
    total = count_scenarios(connection)
    return ScenarioListResponse(
        items=rows,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        locale=build_locale(rows, locale),
    )


@router.post("/scenario-runs", response_model=ScenarioRunResult)
def create_scenario_run(
    payload: ScenarioRunInput,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> ScenarioRunResult:
    rows = run_scenario(
        connection,
        payload.scenario_slug,
        [str(country_id) for country_id in payload.country_ids],
    )
    return ScenarioRunResult(scenario_slug=payload.scenario_slug, results=rows)


@router.get("/scenarios/{slug}", response_model=DecisionScenarioResponse)
def read_scenario_detail(
    slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> DecisionScenarioResponse:
    row = decision_engine.get_scenario(connection, slug, locale)
    return DecisionScenarioResponse(
        item=DecisionScenario(
            id=row["id"],
            slug=row["slug"],
            title=row["title"],
            description=row["description"],
            weights=row["weights"],
        ),
        locale=build_locale([row], locale),
    )


@router.get(
    "/scenarios/{slug}/countries", response_model=DecisionCountryScoreListResponse
)
def read_scenario_countries(
    slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleQuery,
) -> DecisionCountryScoreListResponse:
    items = decision_engine.list_scenario_countries(connection, slug, locale)
    return DecisionCountryScoreListResponse(
        items=items,
        locale=build_locale([item.model_dump() for item in items], locale),
    )
