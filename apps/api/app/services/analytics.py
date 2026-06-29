from app.core.config import Settings
from app.core.errors import api_error
from app.repositories import analytics as analytics_repository
from app.schemas.analytics import AnalyticsEventCreate, AnalyticsEventCreateResponse
import hashlib
import hmac
import json
from psycopg import Connection
from typing import Any


FORBIDDEN_METADATA_KEYS = frozenset(
    {
        "email",
        "phone",
        "name",
        "full_name",
        "telegram_user_id",
        "ip",
        "ip_address",
        "user_agent",
        "token",
        "admin_token",
        "password",
    }
)


def hash_session_id(session_id: str, salt: str) -> str:
    return hmac.new(
        salt.encode("utf-8"),
        session_id.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def validate_no_pii(metadata: dict[str, Any]) -> None:
    forbidden = sorted(
        key for key in metadata if key.lower() in FORBIDDEN_METADATA_KEYS
    )
    if forbidden:
        raise api_error(
            422,
            "analytics_pii_not_allowed",
            "Analytics metadata contains forbidden PII keys.",
            {"keys": forbidden},
        )


def sanitize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    if len(metadata) > 20:
        raise api_error(
            422,
            "analytics_payload_invalid",
            "Analytics metadata contains too many keys.",
            {"max_keys": 20},
        )
    sanitized: dict[str, Any] = {}
    for key, value in metadata.items():
        if len(key) > 64:
            raise api_error(
                422,
                "analytics_payload_invalid",
                "Analytics metadata key is too long.",
                {"max_key_length": 64},
            )
        if isinstance(value, str):
            if len(value) > 256:
                raise api_error(
                    422,
                    "analytics_payload_invalid",
                    "Analytics metadata string value is too long.",
                    {"max_string_length": 256},
                )
            sanitized[key] = value
            continue
        if value is None or isinstance(value, bool | int | float):
            sanitized[key] = value
            continue
        raise api_error(
            422,
            "analytics_payload_invalid",
            "Analytics metadata supports only scalar JSON values.",
            {"key": key},
        )
    if len(json.dumps(sanitized, default=str).encode("utf-8")) > 4096:
        raise api_error(
            422,
            "analytics_payload_invalid",
            "Analytics metadata is too large.",
            {"max_bytes": 4096},
        )
    validate_no_pii(sanitized)
    return sanitized


def record_analytics_event(
    connection: Connection[Any],
    payload: AnalyticsEventCreate,
    settings: Settings,
) -> AnalyticsEventCreateResponse:
    if not settings.analytics_enabled:
        return AnalyticsEventCreateResponse(
            accepted=True,
            stored=False,
            reason="analytics_disabled",
        )
    metadata = sanitize_metadata(payload.metadata)
    session_hash = hash_session_id(payload.session_id, settings.analytics_salt)
    event_id = analytics_repository.insert_analytics_event(
        connection,
        session_hash=session_hash,
        event_type=payload.event_type,
        source=payload.source.value,
        path=payload.path,
        locale=payload.locale,
        country_slug=payload.country_slug,
        scenario_slug=payload.scenario_slug,
        persona_slug=payload.persona_slug,
        route_id=payload.route_id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        metadata=metadata,
    )
    return AnalyticsEventCreateResponse(
        accepted=True,
        stored=True,
        event_id=event_id,
    )
