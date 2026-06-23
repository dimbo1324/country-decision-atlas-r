from app.api.v1 import countries as countries_route
from app.core.locales import get_locale
from app.repositories import decision_engine as decision_repository
from app.schemas.decision_engine import DecisionRunRequest
from app.services import decision_engine
from fastapi import HTTPException
from psycopg import Connection
from tests.test_decision_run import install_repository_fakes
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def assert_error_shape(error: HTTPException, code: str) -> None:
    detail = cast(dict[str, Any], error.detail)
    assert set(detail) == {"error"}
    assert {"code", "message", "details"} == set(detail["error"])
    assert detail["error"]["code"] == code
    assert isinstance(detail["error"]["message"], str)
    assert isinstance(detail["error"]["details"], dict)


def test_unsupported_locale_error_contract() -> None:
    try:
        get_locale("es")
    except HTTPException as error:
        assert error.status_code == 422
        assert_error_shape(error, "unsupported_locale")
    else:
        raise AssertionError("Unsupported locale was accepted")


def test_unknown_country_detail_error_contract(monkeypatch: Any) -> None:
    monkeypatch.setattr(countries_route, "get_country", lambda *_: None)

    try:
        countries_route.read_country("unknown", CONNECTION, get_locale("en"))
    except HTTPException as error:
        assert error.status_code == 404
        assert_error_shape(error, "country_not_found")
    else:
        raise AssertionError("Unknown country was accepted")


def test_unknown_country_card_error_contract(monkeypatch: Any) -> None:
    monkeypatch.setattr(countries_route, "get_country_read_model", lambda *_: None)

    try:
        countries_route.read_country_card("unknown", CONNECTION, get_locale("en"))
    except HTTPException as error:
        assert error.status_code == 404
        assert_error_shape(error, "country_not_found")
    else:
        raise AssertionError("Unknown country card was accepted")


def test_unknown_decision_scenario_error_contract(monkeypatch: Any) -> None:
    install_repository_fakes(monkeypatch)
    monkeypatch.setattr(decision_repository, "get_decision_scenario", lambda *_: None)

    try:
        decision_engine.run_decision(
            CONNECTION,
            DecisionRunRequest(
                origin_country_slug="russia",
                candidate_country_slugs=["uruguay", "russia"],
                scenario_slug="unknown",
            ),
        )
    except HTTPException as error:
        assert error.status_code == 404
        assert_error_shape(error, "scenario_not_found")
    else:
        raise AssertionError("Unknown scenario was accepted")


def test_unknown_decision_country_error_contract(monkeypatch: Any) -> None:
    install_repository_fakes(monkeypatch)

    try:
        decision_engine.run_decision(
            CONNECTION,
            DecisionRunRequest(
                origin_country_slug="unknown",
                candidate_country_slugs=["uruguay", "russia"],
                scenario_slug="relocation_residence",
            ),
        )
    except HTTPException as error:
        assert error.status_code == 404
        assert_error_shape(error, "country_not_found")
    else:
        raise AssertionError("Unknown country was accepted")


def test_duplicate_decision_candidates_error_contract(monkeypatch: Any) -> None:
    install_repository_fakes(monkeypatch)

    try:
        decision_engine.run_decision(
            CONNECTION,
            DecisionRunRequest(
                origin_country_slug="russia",
                candidate_country_slugs=["uruguay", "uruguay"],
                scenario_slug="relocation_residence",
            ),
        )
    except HTTPException as error:
        assert error.status_code == 422
        assert_error_shape(error, "invalid_candidate_countries")
    else:
        raise AssertionError("Duplicate candidates were accepted")
