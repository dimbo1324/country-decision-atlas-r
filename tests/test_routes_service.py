from app.repositories import (
    countries as countries_repository,
    route_checklists as route_checklists_repository,
    routes as routes_repository,
)
from app.services import routes as service
from datetime import UTC, datetime
from fastapi import HTTPException
from psycopg import Connection
import pytest
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())
ROUTE_ID = "11111111-1111-1111-1111-111111111111"
COUNTRY_ID = "22222222-2222-2222-2222-222222222222"
SOURCE_ID = "33333333-3333-3333-3333-333333333333"
EVIDENCE_ID = "44444444-4444-4444-4444-444444444444"
DOCUMENT_ID = "55555555-5555-5555-5555-555555555555"
NOW = datetime(2026, 6, 26, tzinfo=UTC)


class FakeTransaction:
    def __init__(self) -> None:
        self.entered = False
        self.exited = False

    def __enter__(self) -> None:
        self.entered = True

    def __exit__(self, *_: object) -> None:
        self.exited = True


class FakeConnection:
    def __init__(self) -> None:
        self.transactions: list[FakeTransaction] = []

    def transaction(self) -> FakeTransaction:
        transaction = FakeTransaction()
        self.transactions.append(transaction)
        return transaction


def route_row(
    status: str = "published",
    title: str = "Temporary residence",
    summary: str = "Route summary",
    total_count: int = 1,
) -> dict[str, Any]:
    return {
        "id": ROUTE_ID,
        "country_id": COUNTRY_ID,
        "country_slug": "uruguay",
        "route_type": "temporary_residence",
        "slug": "temporary-residence",
        "title": title,
        "summary": summary,
        "eligibility_summary": "Eligibility summary",
        "income_requirement_note": "Income note",
        "fees_note": "Fees note",
        "processing_time_note": "Processing note",
        "stay_period_note": "Stay note",
        "renewal_note": "Renewal note",
        "tax_warning": "Tax warning",
        "legal_warning": "Legal warning",
        "allows_work": "yes",
        "allows_family": "unknown",
        "leads_to_pr": "yes",
        "leads_to_citizenship": "unknown",
        "requires_income_proof": "unknown",
        "requires_local_address": "yes",
        "requires_criminal_record_check": "unknown",
        "legal_status": "effective",
        "status": status,
        "updated_at": NOW,
        "total_count": total_count,
    }


def patch_country_exists(monkeypatch: pytest.MonkeyPatch, exists: bool = True) -> None:
    monkeypatch.setattr(
        countries_repository,
        "get_country",
        lambda *_: {"slug": "uruguay"} if exists else None,
    )


def patch_detail_children(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        routes_repository,
        "list_route_documents",
        lambda *_: [
            {
                "id": DOCUMENT_ID,
                "name": "Passport",
                "is_mandatory": True,
                "note": None,
                "display_order": 1,
            }
        ],
    )
    monkeypatch.setattr(
        routes_repository,
        "list_route_sources",
        lambda *_: [
            {
                "id": SOURCE_ID,
                "title": "Official source",
                "url": "https://example.test",
                "source_type": "official",
                "publisher": "Authority",
                "confidence": "high",
                "country_slug": "uruguay",
            }
        ],
    )
    monkeypatch.setattr(
        routes_repository,
        "list_route_evidence",
        lambda *_: [
            {
                "id": EVIDENCE_ID,
                "source_id": SOURCE_ID,
                "claim": "Claim",
                "excerpt": "Excerpt",
                "confidence": "high",
                "country_slug": "uruguay",
                "source_title": "Official source",
                "source_url": "https://example.test",
            }
        ],
    )
    monkeypatch.setattr(
        route_checklists_repository,
        "list_route_checklist_items",
        lambda *_: [],
    )


def patch_lifecycle(
    monkeypatch: pytest.MonkeyPatch,
    before: dict[str, Any],
    after: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    audit_events: list[dict[str, Any]] = []
    domain_events: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    monkeypatch.setattr(
        routes_repository,
        "get_route_for_admin",
        lambda *_: before,
    )
    monkeypatch.setattr(
        routes_repository,
        "patch_route_status",
        lambda *_: after,
    )
    monkeypatch.setattr(
        service,
        "insert_audit_event",
        lambda _connection, **kwargs: audit_events.append(kwargs),
    )

    def fake_insert_domain_event(_connection: Any, **kwargs: Any) -> None:
        if kwargs["event_key"] in seen_keys:
            return
        seen_keys.add(kwargs["event_key"])
        domain_events.append(kwargs)

    monkeypatch.setattr(service, "insert_domain_event", fake_insert_domain_event)
    return audit_events, domain_events


def assert_error(exc: HTTPException, status_code: int, code: str) -> None:
    detail = cast(dict[str, Any], exc.detail)
    assert exc.status_code == status_code
    assert detail["error"]["code"] == code


def test_list_country_routes_returns_response_with_items(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_country_exists(monkeypatch)
    monkeypatch.setattr(
        routes_repository, "list_routes_by_country", lambda *_: [route_row()]
    )

    result = service.list_country_routes(CONNECTION, "uruguay", "ru")

    assert len(result.items) == 1
    assert result.items[0].eligibility.allows_work == "yes"
    assert result.pagination.total == 1


def test_list_country_routes_unknown_country_raises_country_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_country_exists(monkeypatch, exists=False)

    with pytest.raises(HTTPException) as exc:
        service.list_country_routes(CONNECTION, "missing", "ru")

    assert_error(exc.value, 404, "country_not_found")


def test_list_country_routes_valid_country_without_routes_returns_empty_items(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_country_exists(monkeypatch)
    monkeypatch.setattr(routes_repository, "list_routes_by_country", lambda *_: [])

    result = service.list_country_routes(CONNECTION, "uruguay", "ru")

    assert result.items == []
    assert result.pagination.total == 0


def test_get_route_detail_returns_documents_sources_and_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(routes_repository, "get_route_by_id", lambda *_: route_row())
    patch_detail_children(monkeypatch)

    result = service.get_route_detail(CONNECTION, ROUTE_ID, "ru")

    assert result.documents[0].name == "Passport"
    assert result.sources[0].title == "Official source"
    assert result.evidence[0].claim == "Claim"


def test_get_route_detail_unknown_route_raises_route_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(routes_repository, "get_route_by_id", lambda *_: None)

    with pytest.raises(HTTPException) as exc:
        service.get_route_detail(CONNECTION, ROUTE_ID, "ru")

    assert_error(exc.value, 404, "route_not_found")


def test_locale_ru_uses_repository_ru_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_country_exists(monkeypatch)
    monkeypatch.setattr(
        routes_repository,
        "list_routes_by_country",
        lambda *_: [route_row(title="ВНЖ", summary="Описание")],
    )

    result = service.list_country_routes(CONNECTION, "uruguay", "ru")

    assert result.items[0].title == "ВНЖ"
    assert result.items[0].summary == "Описание"
    assert result.locale.requested_locale == "ru"


def test_locale_en_uses_repository_en_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_country_exists(monkeypatch)
    monkeypatch.setattr(
        routes_repository,
        "list_routes_by_country",
        lambda *_: [route_row(title="Residence", summary="Summary")],
    )

    result = service.list_country_routes(CONNECTION, "uruguay", "en")

    assert result.items[0].title == "Residence"
    assert result.locale.translation_status == "source"


def test_invalid_transition_raises_invalid_publication_transition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = route_row(status="draft")
    after = route_row(status="published")
    patch_lifecycle(monkeypatch, before, after)

    with pytest.raises(HTTPException) as exc:
        service.change_route_status(
            cast(Any, FakeConnection()), ROUTE_ID, "published", "admin"
        )

    assert_error(exc.value, 422, "invalid_publication_transition")


def test_review_to_published_writes_audit_and_domain_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = route_row(status="review")
    after = route_row(status="published")
    audit_events, domain_events = patch_lifecycle(monkeypatch, before, after)

    result = service.change_route_status(
        cast(Any, FakeConnection()), ROUTE_ID, "published", "admin"
    )

    assert result["status"] == "published"
    assert audit_events[0]["action"] == "published"
    assert domain_events[0]["event_key"] == f"route:{ROUTE_ID}:route.published"
    assert domain_events[0]["payload"]["country_slug"] == "uruguay"


def test_repeated_publish_does_not_duplicate_domain_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = route_row(status="archived")
    after = route_row(status="published")
    _, domain_events = patch_lifecycle(monkeypatch, before, after)
    fake_connection = cast(Any, FakeConnection())

    service.change_route_status(fake_connection, ROUTE_ID, "published", "admin")
    service.change_route_status(fake_connection, ROUTE_ID, "published", "admin")

    assert len(domain_events) == 1


def test_ordinary_status_change_not_to_published_writes_audit_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = route_row(status="draft")
    after = route_row(status="review")
    audit_events, domain_events = patch_lifecycle(monkeypatch, before, after)

    service.change_route_status(
        cast(Any, FakeConnection()), ROUTE_ID, "review", "admin"
    )

    assert audit_events[0]["action"] == "submitted_for_review"
    assert domain_events == []


def test_published_to_archived_writes_audit_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = route_row(status="published")
    after = route_row(status="archived")
    audit_events, domain_events = patch_lifecycle(monkeypatch, before, after)

    service.change_route_status(
        cast(Any, FakeConnection()), ROUTE_ID, "archived", "admin"
    )

    assert audit_events[0]["action"] == "archived"
    assert domain_events == []


def test_seeded_routes_do_not_create_route_published_events(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_insert_domain_event(*_: Any, **__: Any) -> None:
        raise AssertionError("domain event should not be inserted by read service")

    patch_country_exists(monkeypatch)
    monkeypatch.setattr(routes_repository, "list_routes_by_country", lambda *_: [])
    monkeypatch.setattr(service, "insert_domain_event", fail_insert_domain_event)

    service.list_country_routes(CONNECTION, "uruguay", "ru")


def test_draft_to_archived_is_not_allowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = route_row(status="draft")
    after = route_row(status="archived")
    patch_lifecycle(monkeypatch, before, after)

    with pytest.raises(HTTPException) as exc:
        service.change_route_status(
            cast(Any, FakeConnection()), ROUTE_ID, "archived", "admin"
        )

    assert_error(exc.value, 422, "invalid_publication_transition")


def test_locale_ru_returns_partial_translation_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_country_exists(monkeypatch)
    monkeypatch.setattr(
        routes_repository,
        "list_routes_by_country",
        lambda *_: [route_row()],
    )

    result = service.list_country_routes(CONNECTION, "uruguay", "ru")

    assert result.locale.translation_status == "fallback"


def test_get_route_detail_by_slug_returns_detail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(routes_repository, "get_route_by_slug", lambda *_: route_row())
    patch_detail_children(monkeypatch)

    result = service.get_route_detail_by_slug(
        CONNECTION, "uruguay", "temporary-residence", "ru"
    )

    assert result.slug == "temporary-residence"


def test_get_route_detail_by_slug_unknown_route_raises_route_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(routes_repository, "get_route_by_slug", lambda *_: None)

    with pytest.raises(HTTPException) as exc:
        service.get_route_detail_by_slug(CONNECTION, "uruguay", "missing", "ru")

    assert_error(exc.value, 404, "route_not_found")
