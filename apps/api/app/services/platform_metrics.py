from app.repositories import platform_metrics as repository
from app.services.contradiction_score import compute_contradiction_score
from app.services.legal_velocity import compute_legal_velocity_index
from app.services.platform_metric_types import (
    METHODOLOGY_VERSION,
    PlatformMetricComputation,
)
from app.services.scenario_risk import compute_scenario_specific_risk_score
from decimal import Decimal
from psycopg import Connection
from typing import Any


MVP_SCENARIO_SLUGS = [
    "relocation_residence",
    "permanent_residence_citizenship",
    "low_budget_living",
    "business_self_employment",
    "safety_political_risk",
]


def compute_country_platform_metrics(
    connection: Connection[Any],
    country_slug: str,
    window_days: int = 365,
    methodology_version: str = METHODOLOGY_VERSION,
) -> list[PlatformMetricComputation]:
    country = repository.get_country_by_slug(connection, country_slug)
    if country is None:
        raise LookupError("Country not found")
    country_id = str(country["id"])
    computations = [
        _with_methodology(
            compute_legal_velocity_index(
                repository.list_legal_velocity_events(
                    connection, country_id, window_days
                ),
                window_days,
            ),
            methodology_version,
        ),
        _with_methodology(
            compute_contradiction_score(
                repository.list_contradiction_inputs(
                    connection, country_id, window_days
                ),
                window_days,
            ),
            methodology_version,
        ),
    ]
    for scenario_slug in _scenario_slugs(connection):
        computations.append(
            _with_methodology(
                compute_scenario_specific_risk_score(
                    repository.list_scenario_risk_inputs(
                        connection, country_id, scenario_slug, window_days
                    ),
                    scenario_slug,
                    window_days,
                ),
                methodology_version,
            )
        )
    return computations


def compute_and_store_country_platform_metrics(
    connection: Connection[Any],
    country_slug: str,
    window_days: int = 365,
    methodology_version: str = METHODOLOGY_VERSION,
) -> list[dict[str, Any]]:
    country = repository.get_country_by_slug(connection, country_slug)
    if country is None:
        raise LookupError("Country not found")
    computations = compute_country_platform_metrics(
        connection, country_slug, window_days, methodology_version
    )
    return [
        _upsert_computation(connection, str(country["id"]), computation)
        for computation in computations
    ]


def compute_and_store_all_country_platform_metrics(
    connection: Connection[Any],
    window_days: int = 365,
    methodology_version: str = METHODOLOGY_VERSION,
) -> list[dict[str, Any]]:
    stored: list[dict[str, Any]] = []
    for country in repository.list_active_countries(connection):
        stored.extend(
            compute_and_store_country_platform_metrics(
                connection,
                str(country["slug"]),
                window_days,
                methodology_version,
            )
        )
    return stored


def _upsert_computation(
    connection: Connection[Any],
    country_id: str,
    computation: PlatformMetricComputation,
) -> dict[str, Any]:
    return repository.upsert_country_platform_metric(
        connection,
        country_id,
        computation.metric_key,
        computation.scenario_slug,
        _value_for_storage(computation.value),
        computation.label,
        computation.confidence,
        computation.freshness_status,
        computation.window_days,
        computation.methodology_version,
        computation.input_summary,
        computation.source_count,
        computation.evidence_count,
        computation.signal_count,
        computation.event_count,
    )


def _value_for_storage(value: Decimal | None) -> Decimal | None:
    return value


def _scenario_slugs(connection: Connection[Any]) -> list[str]:
    rows = repository.list_active_mvp_scenarios(connection)
    slugs = [str(row["slug"]) for row in rows if str(row.get("slug") or "")]
    return slugs or MVP_SCENARIO_SLUGS


def _with_methodology(
    computation: PlatformMetricComputation,
    methodology_version: str,
) -> PlatformMetricComputation:
    if computation.methodology_version == methodology_version:
        return computation
    return PlatformMetricComputation(
        metric_key=computation.metric_key,
        scenario_slug=computation.scenario_slug,
        value=computation.value,
        label=computation.label,
        confidence=computation.confidence,
        freshness_status=computation.freshness_status,
        window_days=computation.window_days,
        methodology_version=methodology_version,
        input_summary=computation.input_summary,
        source_count=computation.source_count,
        evidence_count=computation.evidence_count,
        signal_count=computation.signal_count,
        event_count=computation.event_count,
    )
