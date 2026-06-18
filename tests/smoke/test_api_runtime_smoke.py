import json
import os
import pytest
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "change-me-local-admin-token")
SCENARIOS = [
    "relocation_residence",
    "permanent_residence_citizenship",
    "low_budget_living",
    "business_self_employment",
    "safety_political_risk",
]

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_RUNTIME_SMOKE_TESTS") != "1",
    reason="Runtime smoke tests are disabled.",
)


def request_json(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, Any]]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = Request(
        f"{API_BASE_URL}{path}",
        data=data,
        method=method,
        headers={
            "Accept": "application/json",
            **({"Content-Type": "application/json"} if body is not None else {}),
            **(headers or {}),
        },
    )
    try:
        with urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))


def get_json(path: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    status, body = request_json("GET", path, headers=headers)
    assert status == 200
    return body


def test_health_smoke() -> None:
    body = get_json("/health")
    assert body["status"] == "ok"


@pytest.mark.parametrize("locale", ["en", "ru"])
def test_countries_smoke(locale: str) -> None:
    body = get_json(f"/api/v1/countries?locale={locale}")
    slugs = {item["slug"] for item in body["items"]}
    assert {"russia", "uruguay"}.issubset(slugs)
    assert body["locale"]["requested_locale"] == locale


@pytest.mark.parametrize("country_slug", ["russia", "uruguay"])
@pytest.mark.parametrize("locale", ["en", "ru"])
def test_country_card_smoke(country_slug: str, locale: str) -> None:
    body = get_json(f"/api/v1/countries/{country_slug}/card?locale={locale}")
    assert {
        "country",
        "profile",
        "scores",
        "legal_signals",
        "sources",
        "evidence_summary",
        "user_stories_summary",
        "meta",
        "locale",
    }.issubset(body)
    assert len(body["scores"]) == 5


@pytest.mark.parametrize("scenario_slug", SCENARIOS)
@pytest.mark.parametrize("locale", ["en", "ru"])
def test_decision_run_smoke(scenario_slug: str, locale: str) -> None:
    status, body = request_json(
        "POST",
        "/api/v1/decision/run",
        {
            "origin_country_slug": "russia",
            "candidate_country_slugs": ["uruguay", "russia"],
            "scenario_slug": scenario_slug,
            "locale": locale,
        },
    )
    assert status == 200
    assert {"scenario", "origin_country", "results", "meta", "locale"}.issubset(body)
    assert len(body["results"]) == 2
    for result in body["results"]:
        assert {
            "rank",
            "country",
            "score",
            "score_label",
            "summary",
            "strengths",
            "weaknesses",
            "risk_warnings",
            "confidence",
            "breakdown",
            "sources",
        }.issubset(result)


def test_legal_signals_filter_smoke() -> None:
    body = get_json("/api/v1/legal-signals?country_slug=russia&locale=ru&limit=5")
    assert {"items", "pagination", "sort", "locale"}.issubset(body)


def test_sources_filter_smoke() -> None:
    body = get_json("/api/v1/sources?country_slug=uruguay&limit=5&offset=0")
    assert {"items", "pagination", "sort", "locale"}.issubset(body)


def test_evidence_items_filter_smoke() -> None:
    body = get_json("/api/v1/evidence-items?country_slug=russia&limit=5&offset=0")
    assert {"items", "pagination", "sort"}.issubset(body)


def test_user_stories_filter_smoke() -> None:
    body = get_json("/api/v1/user-stories?destination_country_slug=uruguay&limit=5")
    assert {"items", "pagination"}.issubset(body)


def test_data_quality_report_smoke() -> None:
    body = get_json(
        "/api/v1/admin/data-quality/report",
        headers={"X-Admin-Token": ADMIN_TOKEN},
    )
    assert {"valid", "issues"}.issubset(body)


def test_unsupported_locale_smoke() -> None:
    status, body = request_json("GET", "/api/v1/countries?locale=es")
    assert status in {400, 422}
    assert body["error"]["code"] == "unsupported_locale"
