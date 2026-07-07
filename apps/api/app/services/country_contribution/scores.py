from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import country_contribution as repository
from app.services.country_contribution import helpers
from app.services.methodology_config import get_active_methodology_config
from app.services.score_labels import score_label
from psycopg import Connection
from typing import Any


WEIGHT_SUM_TOLERANCE = 0.01


def upsert_scenario_scores(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    scenario_slug: str,
    breakdowns: list[Any],
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = helpers.get_proposal_or_404(connection, proposal_id)
    scenario_id = repository.get_scenario_id_by_slug(connection, scenario_slug)
    if scenario_id is None:
        raise api_error(
            404, "scenario_not_found", "Scenario was not found.", {}
        )
    _validate_breakdowns(breakdowns)
    overall_score = round(
        sum(float(entry.score) * float(entry.weight) for entry in breakdowns), 2
    )
    confidence = helpers.weakest_confidence(
        [entry.confidence for entry in breakdowns]
    )
    thresholds = get_active_methodology_config(connection).score_labels
    label = score_label(overall_score, thresholds)
    with connection.transaction():
        country_score = repository.upsert_country_score(
            connection,
            country_id=proposal["country_id"],
            scenario_id=scenario_id,
            score=overall_score,
            score_label=label,
            confidence=confidence,
            explanation_en="; ".join(
                entry.explanation_en for entry in breakdowns
            ),
            explanation_ru="; ".join(
                entry.explanation_ru for entry in breakdowns
            ),
        )
        breakdown_rows = repository.replace_breakdowns(
            connection,
            country_score_id=str(country_score["id"]),
            breakdowns=[
                {
                    "criterion": entry.criterion,
                    "score": float(entry.score),
                    "weight": float(entry.weight),
                    "explanation_en": entry.explanation_en,
                    "explanation_ru": entry.explanation_ru,
                    "source_ids": [
                        str(source_id) for source_id in entry.source_ids
                    ],
                    "confidence": entry.confidence,
                }
                for entry in breakdowns
            ],
        )
        helpers._audit(
            connection,
            proposal_id,
            "updated",
            current_user.id,
            {"scenario_scores": {"new": scenario_slug}},
        )
    return {
        "country_score": country_score,
        "breakdowns": breakdown_rows,
    }


def _validate_breakdowns(breakdowns: list[Any]) -> None:
    criteria = [entry.criterion for entry in breakdowns]
    if set(criteria) != set(helpers.SCENARIO_CRITERIA) or len(criteria) != len(
        helpers.SCENARIO_CRITERIA
    ):
        raise api_error(
            422,
            "invalid_scenario_breakdown_criteria",
            "Breakdown must cover each of the seven scenario criteria exactly once.",
            {"required_criteria": list(helpers.SCENARIO_CRITERIA)},
        )
    weight_sum = sum(float(entry.weight) for entry in breakdowns)
    if abs(weight_sum - 1.0) > WEIGHT_SUM_TOLERANCE:
        raise api_error(
            422,
            "invalid_scenario_breakdown_weights",
            "Breakdown weights must sum to 1.0.",
            {"weight_sum": weight_sum},
        )
