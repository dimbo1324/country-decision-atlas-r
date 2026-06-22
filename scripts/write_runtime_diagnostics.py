from __future__ import annotations

from datetime import UTC, datetime
import json
import os
from pathlib import Path
import shutil
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT_DIR / "local-artifacts" / "runtime-diagnostics"
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "change-me-local-admin-token")


Check = tuple[str, str, str, dict[str, Any] | None, dict[str, str] | None]


def read_json_response(response_body: bytes) -> dict[str, Any]:
    text = response_body.decode("utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {
            "error": {
                "code": "non_json_response",
                "message": "The API returned a non-JSON response.",
                "details": {},
            }
        }
    if isinstance(payload, dict):
        return payload
    return {"items": payload}


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
        with urlopen(request, timeout=15) as response:
            return response.status, read_json_response(response.read())
    except HTTPError as error:
        return error.code, read_json_response(error.read())


def write_json(directory: Path, name: str, payload: dict[str, Any]) -> None:
    (directory / name).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def checks() -> list[Check]:
    return [
        ("health.json", "GET", "/health", None, None),
        ("countries_en.json", "GET", "/api/v1/countries?locale=en", None, None),
        ("countries_ru.json", "GET", "/api/v1/countries?locale=ru", None, None),
        (
            "russia_card_ru.json",
            "GET",
            "/api/v1/countries/russia/card?locale=ru",
            None,
            None,
        ),
        (
            "uruguay_card_ru.json",
            "GET",
            "/api/v1/countries/uruguay/card?locale=ru",
            None,
            None,
        ),
        (
            "russia_cii.json",
            "GET",
            "/api/v1/countries/russia/cii?version=v1.0",
            None,
            None,
        ),
        (
            "uruguay_cii.json",
            "GET",
            "/api/v1/countries/uruguay/cii?version=v1.0",
            None,
            None,
        ),
        (
            "countries_compare.json",
            "GET",
            "/api/v1/countries/compare?countries=russia,uruguay&scenario=relocation_residence&locale=ru",
            None,
            None,
        ),
        (
            "countries_matrix.json",
            "GET",
            "/api/v1/countries/matrix?countries=russia,uruguay&scenarios=all&locale=ru",
            None,
            None,
        ),
        (
            "legal_timeline_ru.json",
            "GET",
            "/api/v1/legal-signals/timeline?locale=ru",
            None,
            None,
        ),
        (
            "home_overview_ru.json",
            "GET",
            "/api/v1/home/overview?locale=ru",
            None,
            None,
        ),
        (
            "decision_run_relocation_residence_ru.json",
            "POST",
            "/api/v1/decision/run",
            {
                "origin_country_slug": "russia",
                "candidate_country_slugs": ["uruguay", "russia"],
                "scenario_slug": "relocation_residence",
                "locale": "ru",
            },
            None,
        ),
        (
            "legal_signals_russia_ru.json",
            "GET",
            "/api/v1/legal-signals?country_slug=russia&locale=ru&limit=5&offset=0",
            None,
            None,
        ),
        (
            "sources_uruguay.json",
            "GET",
            "/api/v1/sources?country_slug=uruguay&limit=5&offset=0",
            None,
            None,
        ),
        (
            "evidence_items_russia.json",
            "GET",
            "/api/v1/evidence-items?country_slug=russia&limit=5&offset=0",
            None,
            None,
        ),
        (
            "data_quality_report.json",
            "GET",
            "/api/v1/admin/data-quality/report",
            None,
            {"X-Admin-Token": ADMIN_TOKEN},
        ),
        (
            "country_onboarding_report.json",
            "GET",
            "/api/v1/admin/country-onboarding/report",
            None,
            {"X-Admin-Token": ADMIN_TOKEN},
        ),
    ]


def collect(directory: Path) -> list[dict[str, Any]]:
    summary = []
    for filename, method, path, body, headers in checks():
        status, payload = request_json(method, path, body, headers)
        write_json(directory, filename, payload)
        summary.append(
            {
                "file": filename,
                "method": method,
                "path": path,
                "status": status,
                "ok": 200 <= status < 300,
            }
        )
    return summary


def main() -> None:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    target_dir = RUNTIME_DIR / timestamp
    latest_dir = RUNTIME_DIR / "latest"
    target_dir.mkdir(parents=True, exist_ok=True)

    summary = collect(target_dir)
    write_json(
        target_dir,
        "smoke_summary.json",
        {
            "api_base_url": API_BASE_URL,
            "created_at": timestamp,
            "checks": summary,
            "ok": all(item["ok"] for item in summary),
        },
    )

    if latest_dir.exists():
        shutil.rmtree(latest_dir)
    shutil.copytree(target_dir, latest_dir)


if __name__ == "__main__":
    main()
