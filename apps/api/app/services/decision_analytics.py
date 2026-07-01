from app.core.config import Settings, get_settings
from app.schemas.analytics import AnalyticsEventCreate, AnalyticsSource
from app.services.analytics import record_analytics_event
import logging
from psycopg import Connection
from typing import Any


logger = logging.getLogger(__name__)

MIN_SESSION_ID_LENGTH = 8


def _valid_session_id(session_id: str | None) -> str | None:
    if session_id is None:
        return None
    if len(session_id) < MIN_SESSION_ID_LENGTH:
        return None
    return session_id


def record_custom_weights_used(
    connection: Connection[Any],
    *,
    session_id: str | None,
    scenario_slug: str,
    persona_slug: str | None,
    candidate_count: int,
    criteria_count: int,
    weight_mode: str,
    settings: Settings | None = None,
) -> None:
    valid_session_id = _valid_session_id(session_id)
    if valid_session_id is None:
        return
    try:
        payload = AnalyticsEventCreate(
            event_type="decision_custom_weights_used",
            session_id=valid_session_id,
            source=AnalyticsSource.api,
            scenario_slug=scenario_slug,
            persona_slug=persona_slug,
            metadata={
                "scenario_slug": scenario_slug,
                "persona_slug": persona_slug,
                "candidate_count": candidate_count,
                "criteria_count": criteria_count,
                "weight_mode": weight_mode,
            },
        )
        record_analytics_event(connection, payload, settings or get_settings())
    except Exception as exc:
        logger.warning(
            "Failed to record decision_custom_weights_used analytics event.",
            exc_info=exc,
        )


def record_wizard_completed(
    connection: Connection[Any],
    *,
    session_id: str | None,
    primary_goal: str,
    recommended_scenario_slug: str,
    recommended_persona_slug: str | None,
    confidence: str,
    settings: Settings | None = None,
) -> None:
    valid_session_id = _valid_session_id(session_id)
    if valid_session_id is None:
        return
    try:
        payload = AnalyticsEventCreate(
            event_type="decision_wizard_completed",
            session_id=valid_session_id,
            source=AnalyticsSource.api,
            scenario_slug=recommended_scenario_slug,
            persona_slug=recommended_persona_slug,
            metadata={
                "primary_goal": primary_goal,
                "recommended_scenario_slug": recommended_scenario_slug,
                "recommended_persona_slug": recommended_persona_slug,
                "confidence": confidence,
            },
        )
        record_analytics_event(connection, payload, settings or get_settings())
    except Exception as exc:
        logger.warning(
            "Failed to record decision_wizard_completed analytics event.",
            exc_info=exc,
        )
