from app.repositories import routes as repo
from psycopg import Connection
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())

ROUTE_ROW: dict[str, Any] = {
    "id": "route-id",
    "country_id": "country-id",
    "country_slug": "uruguay",
    "country_name": "Uruguay",
    "route_type": "temporary_residence",
    "slug": "temporary-legal-residence",
    "title": "Temporary legal residence",
    "summary": "Summary",
    "eligibility_summary": "Eligibility",
    "allows_work": "unknown",
    "allows_family": "unknown",
    "leads_to_pr": "yes",
    "leads_to_citizenship": "unknown",
    "requires_income_proof": "unknown",
    "requires_local_address": "unknown",
    "requires_criminal_record_check": "unknown",
    "legal_status": "effective",
    "status": "published",
}


def test_list_routes_by_country_returns_only_published_routes(
    monkeypatch: Any,
) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(_: Any, query: str, params: Any) -> list[dict[str, Any]]:
        captured["query"] = query
        captured["params"] = params
        return [ROUTE_ROW]

    monkeypatch.setattr(repo, "fetch_all", fake_fetch_all)

    result = repo.list_routes_by_country(CONNECTION, "uruguay", "ru")

    assert result == [ROUTE_ROW]
    assert "r.status = 'published'" in captured["query"]
    assert "c.slug = %s" in captured["query"]
    assert "uruguay" in captured["params"]
    assert "COUNT(*) OVER() AS total_count" in captured["query"]


def test_list_routes_by_country_returns_routes_for_russia(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [ROUTE_ROW])

    result = repo.list_routes_by_country(CONNECTION, "russia", "en")

    assert result[0]["status"] == "published"


def test_list_routes_by_country_returns_routes_for_uruguay(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [ROUTE_ROW])

    result = repo.list_routes_by_country(CONNECTION, "uruguay", "en")

    assert result[0]["country_slug"] == "uruguay"


def test_list_routes_by_country_returns_routes_for_argentina(monkeypatch: Any) -> None:
    row = {**ROUTE_ROW, "country_slug": "argentina"}
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [row])

    result = repo.list_routes_by_country(CONNECTION, "argentina", "ru")

    assert result[0]["country_slug"] == "argentina"


def test_list_routes_by_country_filters_route_type(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(_: Any, query: str, params: Any) -> list[dict[str, Any]]:
        captured["query"] = query
        captured["params"] = params
        return [ROUTE_ROW]

    monkeypatch.setattr(repo, "fetch_all", fake_fetch_all)

    repo.list_routes_by_country(
        CONNECTION,
        "uruguay",
        "en",
        route_type="temporary_residence",
    )

    assert "r.route_type = %s" in captured["query"]
    assert "temporary_residence" in captured["params"]


def test_list_routes_by_country_filters_allows_work(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(_: Any, query: str, params: Any) -> list[dict[str, Any]]:
        captured["query"] = query
        captured["params"] = params
        return [ROUTE_ROW]

    monkeypatch.setattr(repo, "fetch_all", fake_fetch_all)

    repo.list_routes_by_country(CONNECTION, "argentina", "en", allows_work="yes")

    assert "r.allows_work = %s" in captured["query"]
    assert "yes" in captured["params"]


def test_list_routes_by_country_filters_allows_family(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(_: Any, query: str, params: Any) -> list[dict[str, Any]]:
        captured["query"] = query
        captured["params"] = params
        return [ROUTE_ROW]

    monkeypatch.setattr(repo, "fetch_all", fake_fetch_all)

    repo.list_routes_by_country(CONNECTION, "russia", "en", allows_family="unknown")

    assert "r.allows_family = %s" in captured["query"]
    assert "unknown" in captured["params"]


def test_list_routes_by_country_filters_leads_to_pr(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(_: Any, query: str, params: Any) -> list[dict[str, Any]]:
        captured["query"] = query
        captured["params"] = params
        return [ROUTE_ROW]

    monkeypatch.setattr(repo, "fetch_all", fake_fetch_all)

    repo.list_routes_by_country(CONNECTION, "uruguay", "en", leads_to_pr="yes")

    assert "r.leads_to_pr = %s" in captured["query"]
    assert "yes" in captured["params"]


def test_get_route_by_id_returns_published_route(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_one(_: Any, query: str, params: Any) -> dict[str, Any]:
        captured["query"] = query
        captured["params"] = params
        return ROUTE_ROW

    monkeypatch.setattr(repo, "fetch_one", fake_fetch_one)

    result = repo.get_route_by_id(CONNECTION, "route-id", "ru")

    assert result == ROUTE_ROW
    assert "r.status = 'published'" in captured["query"]
    assert captured["params"][-1] == "route-id"


def test_get_route_by_id_returns_none_for_missing_route(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_one", lambda *_: None)

    assert repo.get_route_by_id(CONNECTION, "missing", "en") is None


def test_get_route_by_slug_returns_published_route(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_one(_: Any, query: str, params: Any) -> dict[str, Any]:
        captured["query"] = query
        captured["params"] = params
        return ROUTE_ROW

    monkeypatch.setattr(repo, "fetch_one", fake_fetch_one)

    result = repo.get_route_by_slug(
        CONNECTION,
        "uruguay",
        "temporary-legal-residence",
        "ru",
    )

    assert result == ROUTE_ROW
    assert "r.status = 'published'" in captured["query"]
    assert captured["params"][-2:] == ("uruguay", "temporary-legal-residence")


def test_get_route_by_slug_returns_none_for_missing_route(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_one", lambda *_: None)

    assert repo.get_route_by_slug(CONNECTION, "uruguay", "missing", "en") is None


def test_list_route_documents_returns_documents(monkeypatch: Any) -> None:
    rows = [
        {
            "id": "doc-id",
            "route_id": "route-id",
            "name": "Identity document",
            "is_mandatory": True,
            "note": "Verify current procedure.",
            "display_order": 1,
        }
    ]
    monkeypatch.setattr(repo, "fetch_all", lambda *_: rows)

    result = repo.list_route_documents(CONNECTION, "route-id", "ru")

    assert result == rows


def test_list_route_documents_sorted_by_display_order(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_all(_: Any, query: str, params: Any) -> list[dict[str, Any]]:
        captured["query"] = query
        captured["params"] = params
        return []

    monkeypatch.setattr(repo, "fetch_all", fake_fetch_all)

    repo.list_route_documents(CONNECTION, "route-id", "en")

    assert "ORDER BY display_order ASC, name ASC" in captured["query"]
    assert captured["params"][-1] == "route-id"


def test_list_route_sources_returns_linked_sources(monkeypatch: Any) -> None:
    rows = [
        {
            "id": "source-id",
            "title": "Official source",
            "url": "https://example.test",
            "source_type": "official",
            "publisher": "Publisher",
            "confidence": "high",
            "country_slug": "uruguay",
        }
    ]
    captured: dict[str, Any] = {}

    def fake_fetch_all(_: Any, query: str, params: Any) -> list[dict[str, Any]]:
        captured["query"] = query
        captured["params"] = params
        return rows

    monkeypatch.setattr(repo, "fetch_all", fake_fetch_all)

    result = repo.list_route_sources(CONNECTION, "route-id")

    assert result == rows
    assert "JOIN route_sources" not in captured["query"]
    assert "route_sources" in captured["query"]
    assert "s.status = 'published'" in captured["query"]
    assert captured["params"] == ("route-id",)


def test_list_route_evidence_returns_linked_evidence(monkeypatch: Any) -> None:
    rows = [
        {
            "id": "evidence-id",
            "source_id": "source-id",
            "claim": "Claim",
            "excerpt": "Excerpt",
            "confidence": "high",
            "country_slug": "argentina",
            "source_title": "Official source",
            "source_url": "https://example.test",
        }
    ]
    monkeypatch.setattr(repo, "fetch_all", lambda *_: rows)

    result = repo.list_route_evidence(CONNECTION, "route-id")

    assert result == rows


def test_list_route_evidence_returns_empty_safely(monkeypatch: Any) -> None:
    monkeypatch.setattr(repo, "fetch_all", lambda *_: [])

    assert repo.list_route_evidence(CONNECTION, "route-id") == []


def test_public_queries_do_not_return_draft_routes(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    def fake_fetch_one(_: Any, query: str, params: Any) -> None:
        captured["query"] = query
        captured["params"] = params
        return None

    monkeypatch.setattr(repo, "fetch_one", fake_fetch_one)

    repo.get_route_by_id(CONNECTION, "draft-route", "en")

    assert "r.status = 'published'" in captured["query"]


def test_get_route_for_admin_returns_any_status_route(monkeypatch: Any) -> None:
    admin_row = {**ROUTE_ROW, "status": "draft"}
    captured: dict[str, Any] = {}

    def fake_fetch_one(_: Any, query: str, params: Any) -> dict[str, Any]:
        captured["query"] = query
        captured["params"] = params
        return admin_row

    monkeypatch.setattr(repo, "fetch_one", fake_fetch_one)

    result = repo.get_route_for_admin(CONNECTION, "route-id")

    assert result == admin_row
    assert "status = 'published'" not in captured["query"]
    assert captured["params"] == ("route-id",)


def test_patch_route_status_updates_status_only(monkeypatch: Any) -> None:
    admin_row = {**ROUTE_ROW, "status": "archived"}
    captured: dict[str, Any] = {}

    def fake_execute_one(_: Any, query: str, params: Any) -> dict[str, Any]:
        captured["query"] = query
        captured["params"] = params
        return admin_row

    monkeypatch.setattr(repo, "execute_one", fake_execute_one)

    result = repo.patch_route_status(CONNECTION, "route-id", "archived")

    assert result == admin_row
    assert "UPDATE routes" in captured["query"]
    assert "status = %s" in captured["query"]
    assert captured["params"] == ("archived", "route-id")
