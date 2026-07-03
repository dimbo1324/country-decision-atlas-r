"""Persona repository queries: active-only filtering, ordering, and locale-specific names."""

from app.repositories import personas as repo
from psycopg import Connection
import pytest
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())

_PERSONA_EN = {
    "id": "persona-uuid-1",
    "slug": "digital_nomad",
    "name": "Digital nomad",
    "description": "Remote worker focused on digital access, safety, and practical residence options.",
    "is_active": True,
    "display_order": 10,
}

_PERSONA_RU = {
    "id": "persona-uuid-1",
    "slug": "digital_nomad",
    "name": "Цифровой кочевник",
    "description": "Удалённый специалист, которому важны цифровая инфраструктура, безопасность и практичные варианты легального пребывания.",
    "is_active": True,
    "display_order": 10,
}

_SEVEN_PERSONAS = [
    {
        "id": f"id-{i}",
        "slug": s,
        "name": s,
        "description": None,
        "is_active": True,
        "display_order": i * 10,
    }
    for i, s in enumerate(
        [
            "digital_nomad",
            "family",
            "student",
            "entrepreneur",
            "low_budget_migrant",
            "investor",
            "skilled_worker",
        ],
        start=1,
    )
]

_MODIFIER_ROWS = [
    {
        "persona_slug": "digital_nomad",
        "version": "v1.0",
        "metric_id": "metric-uuid-1",
        "metric_slug": "rule_of_law",
        "metric_name": "Rule of Law",
        "modifier": 0.05,
    },
    {
        "persona_slug": "digital_nomad",
        "version": "v1.0",
        "metric_id": "metric-uuid-2",
        "metric_slug": "economic_freedom",
        "metric_name": "Economic Freedom",
        "modifier": 0.05,
    },
    {
        "persona_slug": "digital_nomad",
        "version": "v1.0",
        "metric_id": "metric-uuid-3",
        "metric_slug": "political_stability",
        "metric_name": "Political Stability",
        "modifier": 0.05,
    },
    {
        "persona_slug": "digital_nomad",
        "version": "v1.0",
        "metric_id": "metric-uuid-4",
        "metric_slug": "safety",
        "metric_name": "Physical Safety",
        "modifier": 0.15,
    },
    {
        "persona_slug": "digital_nomad",
        "version": "v1.0",
        "metric_id": "metric-uuid-5",
        "metric_slug": "corruption",
        "metric_name": "Anti-Corruption",
        "modifier": 0.00,
    },
    {
        "persona_slug": "digital_nomad",
        "version": "v1.0",
        "metric_id": "metric-uuid-6",
        "metric_slug": "digital_access",
        "metric_name": "Digital Access",
        "modifier": 0.25,
    },
]

_ACTIVE_METRICS = [
    {
        "id": f"metric-uuid-{i}",
        "slug": s,
        "name": n,
        "polarity": "positive",
        "display_order": i,
    }
    for i, (s, n) in enumerate(
        [
            ("rule_of_law", "Rule of Law"),
            ("economic_freedom", "Economic Freedom"),
            ("political_stability", "Political Stability"),
            ("safety", "Physical Safety"),
            ("corruption", "Anti-Corruption"),
            ("digital_access", "Digital Access"),
        ],
        start=1,
    )
]

_SCENARIO_WEIGHT_ROWS = [
    {
        "scenario_slug": "relocation_residence",
        "version": "v1.0",
        "metric_id": "metric-uuid-1",
        "metric_slug": "rule_of_law",
        "base_weight": 0.20,
    },
    {
        "scenario_slug": "relocation_residence",
        "version": "v1.0",
        "metric_id": "metric-uuid-2",
        "metric_slug": "economic_freedom",
        "base_weight": 0.10,
    },
]

_WEIGHT_INPUT_ROWS = [
    {
        "metric_id": "metric-uuid-1",
        "metric_slug": "rule_of_law",
        "metric_name": "Rule of Law",
        "base_weight": 0.20,
        "modifier": 0.05,
    },
    {
        "metric_id": "metric-uuid-4",
        "metric_slug": "safety",
        "metric_name": "Physical Safety",
        "base_weight": 0.25,
        "modifier": 0.15,
    },
]


def test_list_personas_returns_active_only(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(_: Any, query: str, params: Any) -> list[dict[str, Any]]:
        captured["query"] = query
        captured["params"] = params
        return [_PERSONA_EN]

    monkeypatch.setattr(repo, "fetch_all", fake_fetch_all)
    result = repo.list_personas(CONNECTION, "en")

    assert len(result) == 1
    assert result[0]["slug"] == "digital_nomad"
    assert "is_active = TRUE" in captured["query"]


def test_list_personas_returns_7_personas(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_a, **_k: _SEVEN_PERSONAS)
    result = repo.list_personas(CONNECTION, "ru")
    assert len(result) == 7


def test_list_personas_sorted_by_display_order(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(_: Any, query: str, _params: Any) -> list[dict[str, Any]]:
        captured["query"] = query
        return _SEVEN_PERSONAS

    monkeypatch.setattr(repo, "fetch_all", fake_fetch_all)
    repo.list_personas(CONNECTION, "en")
    assert "display_order" in captured["query"]


def test_list_personas_locale_ru_uses_russian_name(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(_: Any, query: str, params: Any) -> list[dict[str, Any]]:
        captured["query"] = query
        captured["params"] = params
        return [_PERSONA_RU]

    monkeypatch.setattr(repo, "fetch_all", fake_fetch_all)
    result = repo.list_personas(CONNECTION, "ru")

    assert result[0]["name"] == "Цифровой кочевник"
    assert "ru" in str(captured["params"]).lower() or "locale" in captured["query"]


def test_list_personas_locale_en_uses_english_name(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_a, **_k: [_PERSONA_EN])
    result = repo.list_personas(CONNECTION, "en")
    assert result[0]["name"] == "Digital nomad"


def test_get_persona_by_slug_returns_existing_persona(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_one", lambda *_a, **_k: _PERSONA_EN)
    result = repo.get_persona_by_slug(CONNECTION, "digital_nomad", "en")
    assert result is not None
    assert result["slug"] == "digital_nomad"


def test_get_persona_by_slug_returns_none_for_unknown(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_one", lambda *_a, **_k: None)
    result = repo.get_persona_by_slug(CONNECTION, "nonexistent", "en")
    assert result is None


def test_list_persona_modifiers_returns_one_row_per_active_metric(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_a, **_k: _MODIFIER_ROWS)
    result = repo.list_persona_modifiers(CONNECTION, "digital_nomad")
    assert len(result) == 6


def test_list_persona_modifiers_returns_modifiers_for_digital_nomad(
    monkeypatch: Any,
) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(_: Any, _query: str, params: Any) -> list[dict[str, Any]]:
        captured["params"] = params
        return _MODIFIER_ROWS

    monkeypatch.setattr(repo, "fetch_all", fake_fetch_all)
    result = repo.list_persona_modifiers(CONNECTION, "digital_nomad")

    assert all(r["persona_slug"] == "digital_nomad" for r in result)
    digital_access_row = next(r for r in result if r["metric_slug"] == "digital_access")
    assert float(digital_access_row["modifier"]) == pytest.approx(0.25)


def test_list_active_persona_slugs_returns_7_slugs(monkeypatch: Any) -> None:
    slugs = [p["slug"] for p in _SEVEN_PERSONAS]
    monkeypatch.setattr(
        repo, "fetch_all", lambda *_a, **_k: [{"slug": s} for s in slugs]
    )
    result = repo.list_active_persona_slugs(CONNECTION)
    assert len(result) == 7
    assert "digital_nomad" in result


def test_list_active_cii_metrics_returns_expected_metrics(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_a, **_k: _ACTIVE_METRICS)
    result = repo.list_active_cii_metrics(CONNECTION)
    slugs = [r["slug"] for r in result]
    assert "rule_of_law" in slugs
    assert "digital_access" in slugs
    assert len(result) == 6


def test_list_base_scenario_weights_returns_rows_for_relocation_residence(
    monkeypatch: Any,
) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(_: Any, _query: str, params: Any) -> list[dict[str, Any]]:
        captured["params"] = params
        return _SCENARIO_WEIGHT_ROWS

    monkeypatch.setattr(repo, "fetch_all", fake_fetch_all)
    result = repo.list_base_scenario_weights(CONNECTION, "relocation_residence")

    assert len(result) == 2
    assert all(r["scenario_slug"] == "relocation_residence" for r in result)


def test_list_base_scenario_weights_does_not_mutate_stored_weights(
    monkeypatch: Any,
) -> None:
    original_weight = _SCENARIO_WEIGHT_ROWS[0]["base_weight"]
    monkeypatch.setattr(repo, "fetch_all", lambda *_a, **_k: _SCENARIO_WEIGHT_ROWS)
    repo.list_base_scenario_weights(CONNECTION, "relocation_residence")
    assert _SCENARIO_WEIGHT_ROWS[0]["base_weight"] == original_weight


def test_list_persona_weight_inputs_includes_base_weight_and_modifier(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_a, **_k: _WEIGHT_INPUT_ROWS)
    result = repo.list_persona_weight_inputs(
        CONNECTION, "relocation_residence", "digital_nomad"
    )

    assert len(result) == 2
    assert all("base_weight" in r for r in result)
    assert all("modifier" in r for r in result)


def test_list_persona_weight_inputs_exposes_missing_modifier_as_none(
    monkeypatch: Any,
) -> None:
    rows_with_missing = [
        {**_WEIGHT_INPUT_ROWS[0], "modifier": None},
        {**_WEIGHT_INPUT_ROWS[1]},
    ]
    monkeypatch.setattr(repo, "fetch_all", lambda *_a, **_k: rows_with_missing)
    result = repo.list_persona_weight_inputs(
        CONNECTION, "relocation_residence", "digital_nomad"
    )
    assert result[0]["modifier"] is None
    assert result[1]["modifier"] is not None
