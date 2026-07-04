from app.core.errors import api_error
from app.repositories import weight_profiles as repository
from app.services.decision_criteria import DECISION_CRITERIA
from app.services.decision_personalization import validate_custom_weights
from decimal import Decimal
from psycopg import Connection, errors as psycopg_errors
from typing import Any, NoReturn


def list_user_weight_profiles(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    return [
        _profile(row)
        for row in repository.list_profiles_for_user(connection, user_id)
    ]


def get_user_weight_profile(
    connection: Connection[Any], profile_id: str, user_id: str
) -> dict[str, Any]:
    row = repository.get_profile_for_user(connection, profile_id, user_id)
    if row is None:
        raise api_error(
            404,
            "weight_profile_not_found",
            "Weight profile was not found.",
            {"weight_profile_id": profile_id},
        )
    return _profile(row)


def create_user_weight_profile(
    connection: Connection[Any],
    *,
    user_id: str,
    name: str,
    scenario_slug: str | None,
    weights: dict[str, Decimal],
    is_default: bool,
) -> dict[str, Any]:
    clean_name = _validate_name(name)
    _validate_scenario(connection, scenario_slug)
    clean_weights = _validate_weights(weights)
    _ensure_name_available(connection, user_id, clean_name, None)
    if is_default:
        repository.clear_default_profiles(connection, user_id, scenario_slug)
    try:
        row = repository.create_profile(
            connection,
            user_id=user_id,
            name=clean_name,
            scenario_slug=scenario_slug,
            weights=clean_weights,
            is_default=is_default,
        )
    except psycopg_errors.UniqueViolation:
        _raise_name_conflict(clean_name)
    return _profile(row)


def update_user_weight_profile(
    connection: Connection[Any],
    *,
    user_id: str,
    profile_id: str,
    fields: set[str],
    name: str | None,
    scenario_slug: str | None,
    weights: dict[str, Decimal] | None,
    is_default: bool | None,
) -> dict[str, Any]:
    existing = get_user_weight_profile(connection, profile_id, user_id)
    next_name = (
        _validate_name(name)
        if "name" in fields and name is not None
        else existing["name"]
    )
    if "name" in fields and name is None:
        raise api_error(
            422,
            "weight_profile_name_required",
            "Weight profile name is required.",
            {},
        )
    next_scenario_slug = (
        scenario_slug
        if "scenario_slug" in fields
        else existing["scenario_slug"]
    )
    _validate_scenario(connection, next_scenario_slug)
    next_weights = (
        _validate_weights(weights)
        if "weights" in fields and weights is not None
        else existing["weights"]
    )
    if "weights" in fields and weights is None:
        raise api_error(
            422,
            "weight_profile_weights_required",
            "Weight profile weights are required.",
            {},
        )
    next_is_default = (
        bool(is_default)
        if "is_default" in fields and is_default is not None
        else existing["is_default"]
    )
    _ensure_name_available(connection, user_id, next_name, profile_id)
    if next_is_default:
        repository.clear_default_profiles(
            connection, user_id, next_scenario_slug
        )
    try:
        row = repository.update_profile(
            connection,
            profile_id=profile_id,
            user_id=user_id,
            name=next_name,
            scenario_slug=next_scenario_slug,
            weights=next_weights,
            is_default=next_is_default,
        )
    except psycopg_errors.UniqueViolation:
        _raise_name_conflict(next_name)
    if row is None:
        raise api_error(
            404,
            "weight_profile_not_found",
            "Weight profile was not found.",
            {"weight_profile_id": profile_id},
        )
    return _profile(row)


def delete_user_weight_profile(
    connection: Connection[Any], profile_id: str, user_id: str
) -> None:
    if not repository.delete_profile(connection, profile_id, user_id):
        raise api_error(
            404,
            "weight_profile_not_found",
            "Weight profile was not found.",
            {"weight_profile_id": profile_id},
        )


def resolve_profile_for_decision(
    connection: Connection[Any],
    *,
    profile_id: str,
    user_id: str,
    scenario_slug: str,
) -> dict[str, Any]:
    profile = get_user_weight_profile(connection, profile_id, user_id)
    profile_scenario = profile.get("scenario_slug")
    if profile_scenario is not None and profile_scenario != scenario_slug:
        raise api_error(
            422,
            "weight_profile_scenario_mismatch",
            "Weight profile cannot be used for this decision scenario.",
            {
                "weight_profile_id": profile_id,
                "profile_scenario_slug": profile_scenario,
                "scenario_slug": scenario_slug,
            },
        )
    return profile


def _validate_name(name: str) -> str:
    clean_name = name.strip()
    if not clean_name:
        raise api_error(
            422,
            "weight_profile_name_required",
            "Weight profile name is required.",
            {},
        )
    if len(clean_name) > 120:
        raise api_error(
            422,
            "weight_profile_name_too_long",
            "Weight profile name is too long.",
            {"max_length": 120},
        )
    return clean_name


def _validate_scenario(
    connection: Connection[Any], scenario_slug: str | None
) -> None:
    if scenario_slug is None:
        return
    if not scenario_slug.strip():
        raise api_error(
            422,
            "weight_profile_scenario_invalid",
            "Weight profile scenario slug is invalid.",
            {},
        )
    if not repository.scenario_exists(connection, scenario_slug):
        raise api_error(
            404,
            "scenario_not_found",
            "Scenario was not found.",
            {"scenario_slug": scenario_slug},
        )


def _validate_weights(weights: dict[str, Decimal] | None) -> dict[str, float]:
    if weights is None:
        raise api_error(
            422,
            "weight_profile_weights_required",
            "Weight profile weights are required.",
            {},
        )
    validate_custom_weights(weights, DECISION_CRITERIA)
    return {
        criterion: float(Decimal(str(value)))
        for criterion, value in sorted(weights.items())
    }


def _ensure_name_available(
    connection: Connection[Any],
    user_id: str,
    name: str,
    profile_id: str | None,
) -> None:
    existing = repository.get_profile_by_name_for_user(
        connection, user_id, name
    )
    if existing is None or str(existing["id"]) == str(profile_id):
        return
    _raise_name_conflict(name)


def _raise_name_conflict(name: str) -> NoReturn:
    raise api_error(
        409,
        "weight_profile_name_exists",
        "A weight profile with this name already exists.",
        {"name": name},
    )


def _profile(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "user_id": str(row["user_id"]),
        "name": row["name"],
        "scenario_slug": row.get("scenario_slug"),
        "weights": {
            str(criterion): float(value)
            for criterion, value in dict(row.get("weights") or {}).items()
        },
        "is_default": bool(row["is_default"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
