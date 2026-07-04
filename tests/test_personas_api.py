"""Persona listing and detail API, including the normalized weight-profile endpoint."""

import pytest
from app.api.v1 import personas as personas_route
from app.repositories import personas as personas_repository
from fastapi import HTTPException
from psycopg import Connection
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = cast(Connection[Any], MagicMock())


PERSONA = {
    "id": "persona-id",
    "slug": "digital_nomad",
    "name": "Digital nomad",
    "description": "Remote worker.",
    "is_active": True,
    "display_order": 10,
}


PROFILE = {
    "persona": PERSONA,
    "scenario_slug": "relocation_residence",
    "version": "v1.0",
    "weights": [
        {
            "metric_id": "m1",
            "metric_slug": "rule_of_law",
            "metric_name": "Rule of Law",
            "base_weight": 0.4,
            "modifier": 0.0,
            "adjusted_weight": 0.4,
        },
        {
            "metric_id": "m2",
            "metric_slug": "safety",
            "metric_name": "Physical Safety",
            "base_weight": 0.6,
            "modifier": 0.0,
            "adjusted_weight": 0.6,
        },
    ],
    "weight_sum": 1.0,
}


def test_personas_list_returns_active_personas(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        personas_repository,
        "list_personas",
        lambda *_: [
            {**PERSONA, "resolved_locale": "en", "translation_status": "source"}
        ],
    )

    result = personas_route.read_personas(CONNECTION, "en")

    assert len(result.items) == 1
    assert result.items[0].slug == "digital_nomad"
    assert result.locale.requested_locale == "en"


def test_persona_detail_unknown_slug_returns_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        personas_repository, "get_persona_by_slug", lambda *_: None
    )

    with pytest.raises(HTTPException) as exc_info:
        personas_route.read_persona("unknown", CONNECTION, "en")

    detail = cast(dict[str, Any], exc_info.value.detail)
    assert exc_info.value.status_code == 404
    assert detail["error"]["code"] == "persona_not_found"


def test_persona_weight_profile_endpoint_returns_normalized_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        personas_route,
        "build_persona_weight_profile",
        lambda *_: PROFILE,
    )

    result = personas_route.read_persona_weights(
        "digital_nomad", "relocation_residence", CONNECTION, "en"
    )

    assert result.item.persona.slug == "digital_nomad"
    assert result.item.weight_sum == pytest.approx(1.0)
    assert sum(
        weight.adjusted_weight for weight in result.item.weights
    ) == pytest.approx(1.0)
