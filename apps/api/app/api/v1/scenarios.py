from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from psycopg import Connection

from app.core.database import get_connection
from app.repositories.common import build_locale
from app.repositories.scenarios import count_scenarios, list_scenarios
from app.repositories.scores import run_scenario
from app.schemas.common import LocaleCode, Pagination
from app.schemas.countries import ScenarioRunInput, ScenarioRunResult
from app.schemas.decision_engine import DecisionCountryScore, DecisionScenario
from app.schemas.scenarios import ScenarioListResponse
from app.services import decision_engine

router = APIRouter(tags=["scenarios"])


@router.get("/scenarios", response_model=ScenarioListResponse)
async def read_scenarios(
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleCode = "en",
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
async def create_scenario_run(
    payload: ScenarioRunInput,
    connection: Annotated[Connection[Any], Depends(get_connection)],
) -> ScenarioRunResult:
    rows = run_scenario(
        connection,
        payload.scenario_slug,
        [str(country_id) for country_id in payload.country_ids],
    )
    return ScenarioRunResult(scenario_slug=payload.scenario_slug, results=rows)


@router.get("/scenarios/{slug}", response_model=DecisionScenario)
async def read_scenario_detail(
    slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleCode = "en",
) -> DecisionScenario:
    row = decision_engine.get_scenario(connection, slug, locale)
    return DecisionScenario(
        id=row["id"],
        slug=row["slug"],
        title=row["title"],
        description=row["description"],
        weights=row["weights"],
    )


@router.get("/scenarios/{slug}/countries", response_model=list[DecisionCountryScore])
async def read_scenario_countries(
    slug: str,
    connection: Annotated[Connection[Any], Depends(get_connection)],
    locale: LocaleCode = "en",
) -> list[DecisionCountryScore]:
    return decision_engine.list_scenario_countries(connection, slug, locale)
