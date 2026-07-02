from app.repositories import route_checklists as repository
from app.services import route_checklists as service, routes as routes_service
from datetime import UTC, datetime
import inspect
from psycopg import Connection
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())
NOW = datetime(2026, 6, 1, tzinfo=UTC)
ROUTE_ID = "11111111-1111-1111-1111-111111111111"


def _checklist_row(**overrides: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": "22222222-2222-2222-2222-222222222222",
        "route_id": ROUTE_ID,
        "step_order": 1,
        "title": "Confirm the procedure",
        "description": "Review the official procedure page.",
        "document_note": None,
        "cost_note": None,
        "timing_note": None,
        "official_requirement_note": None,
        "is_required": True,
        "source_id": "33333333-3333-3333-3333-333333333333",
        "evidence_item_id": None,
    }
    row.update(overrides)
    return row


def test_list_route_checklist_items_filters_published_only() -> None:
    sql_source = inspect.getsource(repository.list_route_checklist_items)
    assert "rci.status = 'published'" in sql_source


def test_list_route_checklist_items_sorted_by_step_order() -> None:
    sql_source = inspect.getsource(repository.list_route_checklist_items)
    assert "ORDER BY rci.step_order" in sql_source


def test_list_route_checklist_items_by_slug_filters_published_only() -> None:
    sql_source = inspect.getsource(repository.list_route_checklist_items_by_route_slug)
    assert "rci.status = 'published'" in sql_source
    assert "ORDER BY rci.step_order" in sql_source


def test_get_route_checklist_returns_items(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        repository, "list_route_checklist_items", lambda *_: [_checklist_row()]
    )

    response = service.get_route_checklist(CONNECTION, ROUTE_ID, "en")

    assert len(response.items) == 1
    assert response.items[0].source_id is not None


def test_get_route_checklist_returns_empty_list_for_route_without_checklist(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(repository, "list_route_checklist_items", lambda *_: [])

    response = service.get_route_checklist(CONNECTION, ROUTE_ID, "en")

    assert response.items == []


def test_get_route_checklist_by_slug_returns_items(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        repository,
        "list_route_checklist_items_by_route_slug",
        lambda *_: [
            _checklist_row(),
            _checklist_row(step_order=2, id="44444444-4444-4444-4444-444444444444"),
        ],
    )

    response = service.get_route_checklist_by_slug(
        CONNECTION, "uruguay", "temporary-legal-residence", "en"
    )

    assert [item.step_order for item in response.items] == [1, 2]


def _route_row() -> dict[str, Any]:
    return {
        "id": ROUTE_ID,
        "country_slug": "uruguay",
        "route_type": "temporary_residence",
        "slug": "temporary-legal-residence",
        "title": "Temporary residence",
        "summary": "Summary",
        "eligibility_summary": "Eligibility",
        "income_requirement_note": None,
        "fees_note": None,
        "processing_time_note": None,
        "stay_period_note": None,
        "renewal_note": None,
        "tax_warning": None,
        "legal_warning": None,
        "allows_work": "yes",
        "allows_family": "unknown",
        "leads_to_pr": "unknown",
        "leads_to_citizenship": "unknown",
        "requires_income_proof": "unknown",
        "requires_local_address": "unknown",
        "requires_criminal_record_check": "unknown",
        "legal_status": "effective",
        "status": "published",
        "updated_at": NOW,
    }


def test_route_detail_includes_checklist(monkeypatch: Any) -> None:
    from app.repositories import routes as routes_repository

    monkeypatch.setattr(routes_repository, "get_route_by_id", lambda *_: _route_row())
    monkeypatch.setattr(routes_repository, "list_route_documents", lambda *_: [])
    monkeypatch.setattr(routes_repository, "list_route_sources", lambda *_: [])
    monkeypatch.setattr(routes_repository, "list_route_evidence", lambda *_: [])
    monkeypatch.setattr(
        repository, "list_route_checklist_items", lambda *_: [_checklist_row()]
    )

    detail = routes_service.get_route_detail(CONNECTION, ROUTE_ID, "en")

    assert len(detail.checklist) == 1
    assert detail.checklist[0].title == "Confirm the procedure"


def test_route_detail_returns_empty_checklist_when_none_seeded(
    monkeypatch: Any,
) -> None:
    from app.repositories import routes as routes_repository

    monkeypatch.setattr(routes_repository, "get_route_by_id", lambda *_: _route_row())
    monkeypatch.setattr(routes_repository, "list_route_documents", lambda *_: [])
    monkeypatch.setattr(routes_repository, "list_route_sources", lambda *_: [])
    monkeypatch.setattr(routes_repository, "list_route_evidence", lambda *_: [])
    monkeypatch.setattr(repository, "list_route_checklist_items", lambda *_: [])

    detail = routes_service.get_route_detail(CONNECTION, ROUTE_ID, "en")

    assert detail.checklist == []
