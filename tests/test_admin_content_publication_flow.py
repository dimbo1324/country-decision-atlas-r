"""Audit log and domain-event side effects of moving legal signals through the editorial publication lifecycle."""

import pytest
from app.repositories import (
    admin_content as admin_repository,
    search_index as search_index_repository,
)
from app.schemas.admin_content import (
    CountryProfilePatch,
    EvidenceItemCreate,
    EvidenceItemPatch,
    LegalSignalPatch,
    SourceCreate,
    SourcePatch,
)
from app.schemas.common import PublicationStatus
from app.services import admin_content
from fastapi import HTTPException
from typing import Any, cast
from uuid import uuid4


class FakeTransaction:
    def __init__(self) -> None:
        self.entered = False
        self.exited = False
        self.failed = False

    def __enter__(self) -> "FakeTransaction":
        self.entered = True
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.exited = True
        self.failed = exc_type is not None


class FakeConnection:
    def __init__(self) -> None:
        self.transactions: list[FakeTransaction] = []

    def transaction(self) -> FakeTransaction:
        transaction = FakeTransaction()
        self.transactions.append(transaction)
        return transaction


def legal_signal_row(status: str, **overrides: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": str(uuid4()),
        "country_id": str(uuid4()),
        "source_id": str(uuid4()),
        "title": "Residency update",
        "summary": "Summary",
        "title_en": "Residency update",
        "title_ru": "Обновление ВНЖ",
        "summary_en": "Summary",
        "summary_ru": "Описание",
        "signal_type": "residence",
        "impact_direction": "positive",
        "impact_level": "medium",
        "legal_status": "effective",
        "affected_groups": [],
        "published_date": None,
        "effective_date": None,
        "confidence": "medium",
        "status": status,
    }
    return {**row, **overrides}


def source_row(status: str = "review", **overrides: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": str(uuid4()),
        "country_id": str(uuid4()),
        "title": "Official source",
        "url": "https://example.org/source",
        "source_type": "official",
        "publisher": "Publisher",
        "language": "en",
        "confidence": "high",
        "status": status,
    }
    return {**row, **overrides}


def evidence_row(status: str = "review", **overrides: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": str(uuid4()),
        "source_id": str(uuid4()),
        "country_id": str(uuid4()),
        "legal_signal_id": str(uuid4()),
        "claim": "Claim",
        "excerpt": "Excerpt",
        "url": "https://example.org/evidence",
        "confidence": "medium",
        "status": status,
    }
    return {**row, **overrides}


def country_profile_row(
    status: str = "review", **overrides: Any
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": str(uuid4()),
        "country_id": str(uuid4()),
        "locale": "en",
        "executive_summary": "Summary",
        "migration_overview": "Migration",
        "tax_overview": "Tax",
        "cost_of_living_overview": "Cost",
        "business_overview": "Business",
        "safety_overview": "Safety",
        "legal_signals_summary": "Legal",
        "risk_summary": "Risk",
        "source_summary": "Sources",
        "status": status,
    }
    return {**row, **overrides}


@pytest.fixture(autouse=True)
def stub_search_index(
    monkeypatch: pytest.MonkeyPatch,
) -> dict[str, list[dict[str, Any]]]:
    """Every admin_content write now syncs the search index in the same
    transaction (P1-7, Аудит-эпизод 5), so every test in this file needs a
    country lookup and a search_index repository stub even if it isn't
    asserting on search-index behavior itself — autouse keeps that plumbing
    out of tests that don't care, while tests that do can still request this
    fixture by name to inspect the captured calls."""
    calls: dict[str, list[dict[str, Any]]] = {"upsert": [], "delete": []}
    monkeypatch.setattr(
        admin_repository, "get_country_slug_by_id", lambda *_: "argentina"
    )
    monkeypatch.setattr(
        admin_repository, "get_country_name_by_id", lambda *_: "Argentina"
    )

    def fake_upsert(_conn: Any, **kwargs: Any) -> dict[str, Any]:
        calls["upsert"].append(kwargs)
        return kwargs

    def fake_delete(
        _conn: Any, entity_type: str, entity_id: str, locale: str
    ) -> int:
        calls["delete"].append(
            {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "locale": locale,
            }
        )
        return 1

    monkeypatch.setattr(
        search_index_repository, "upsert_search_document", fake_upsert
    )
    monkeypatch.setattr(
        search_index_repository, "delete_search_document", fake_delete
    )
    return calls


def patch_audit(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    def fake_insert_audit_event(_: Any, **kwargs: Any) -> dict[str, Any]:
        events.append(kwargs)
        return kwargs

    monkeypatch.setattr(
        admin_content, "insert_audit_event", fake_insert_audit_event
    )
    return events


def patch_domain_events(
    monkeypatch: pytest.MonkeyPatch,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    def fake_insert_domain_event(_: Any, **kwargs: Any) -> dict[str, Any]:
        events.append(kwargs)
        return kwargs

    monkeypatch.setattr(
        admin_content, "insert_domain_event", fake_insert_domain_event
    )
    return events


def test_legal_signal_review_to_published_writes_audit_and_domain_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = legal_signal_row("review")
    after = {**before, "status": "published"}
    rows = [before, after]
    transition_calls: list[tuple[str, str]] = []
    audit_events = patch_audit(monkeypatch)
    domain_events = patch_domain_events(monkeypatch)

    monkeypatch.setattr(
        admin_repository,
        "get_legal_signal_for_admin",
        lambda *_: rows.pop(0),
    )
    monkeypatch.setattr(
        admin_repository,
        "patch_legal_signal",
        lambda *_: after,
    )
    monkeypatch.setattr(
        admin_repository,
        "get_source_for_admin",
        lambda *_: source_row("published"),
    )
    monkeypatch.setattr(
        admin_repository,
        "get_country_slug_by_id",
        lambda *_: "argentina",
    )

    def fake_ensure_allowed_transition(
        old_status: str, new_status: str
    ) -> None:
        transition_calls.append((old_status, new_status))

    monkeypatch.setattr(
        admin_content,
        "ensure_allowed_transition",
        fake_ensure_allowed_transition,
    )

    result = admin_content.patch_legal_signal(
        cast(Any, FakeConnection()),
        str(before["id"]),
        LegalSignalPatch(status=PublicationStatus.published),
        "admin",
    )

    assert result["status"] == "published"
    assert transition_calls == [("review", "published")]
    assert audit_events[0]["action"] == "published"
    assert audit_events[0]["changes"]["status"] == {
        "old": "review",
        "new": "published",
    }
    assert len(domain_events) == 1
    assert domain_events[0]["event_key"] == (
        f"legal_signal:{before['id']}:legal_signal.published"
    )
    assert domain_events[0]["payload"]["legal_status"] == "effective"


def test_repeated_publish_does_not_create_second_domain_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = legal_signal_row("published")
    after = {**before, "summary_en": "Updated summary"}
    rows = [before, after]
    patch_audit(monkeypatch)
    domain_events = patch_domain_events(monkeypatch)
    monkeypatch.setattr(
        admin_repository,
        "get_legal_signal_for_admin",
        lambda *_: rows.pop(0),
    )
    monkeypatch.setattr(
        admin_repository,
        "patch_legal_signal",
        lambda *_: after,
    )
    monkeypatch.setattr(
        admin_repository,
        "get_source_for_admin",
        lambda *_: source_row("published"),
    )

    admin_content.patch_legal_signal(
        cast(Any, FakeConnection()),
        str(before["id"]),
        LegalSignalPatch(summary_en="Updated summary"),
        "admin",
    )

    assert domain_events == []


def test_legal_signal_draft_to_published_returns_invalid_transition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = legal_signal_row("draft")
    patch_calls: list[str] = []
    audit_events = patch_audit(monkeypatch)
    domain_events = patch_domain_events(monkeypatch)
    monkeypatch.setattr(
        admin_repository,
        "get_legal_signal_for_admin",
        lambda *_: before,
    )
    monkeypatch.setattr(
        admin_repository,
        "patch_legal_signal",
        lambda *_: patch_calls.append("patch"),
    )

    with pytest.raises(HTTPException) as exc:
        admin_content.patch_legal_signal(
            cast(Any, FakeConnection()),
            str(before["id"]),
            LegalSignalPatch(status=PublicationStatus.published),
            "admin",
        )

    assert exc.value.status_code == 422
    detail = cast(dict[str, Any], exc.value.detail)
    assert detail["error"]["code"] == "invalid_publication_transition"
    assert patch_calls == []
    assert audit_events == []
    assert domain_events == []


def test_ordinary_legal_signal_patch_writes_audit_without_domain_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = legal_signal_row("review")
    after = {**before, "title_en": "Updated title"}
    rows = [before, after]
    audit_events = patch_audit(monkeypatch)
    domain_events = patch_domain_events(monkeypatch)
    monkeypatch.setattr(
        admin_repository,
        "get_legal_signal_for_admin",
        lambda *_: rows.pop(0),
    )
    monkeypatch.setattr(
        admin_repository,
        "patch_legal_signal",
        lambda *_: after,
    )

    admin_content.patch_legal_signal(
        cast(Any, FakeConnection()),
        str(before["id"]),
        LegalSignalPatch(title_en="Updated title"),
        "admin",
    )

    assert audit_events[0]["action"] == "updated"
    assert audit_events[0]["changes"]["title_en"]["new"] == "Updated title"
    assert domain_events == []


def test_legal_signal_published_to_archived_writes_audit_without_domain_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = legal_signal_row("published")
    after = {**before, "status": "archived"}
    rows = [before, after]
    audit_events = patch_audit(monkeypatch)
    domain_events = patch_domain_events(monkeypatch)
    monkeypatch.setattr(
        admin_repository,
        "get_legal_signal_for_admin",
        lambda *_: rows.pop(0),
    )
    monkeypatch.setattr(
        admin_repository,
        "patch_legal_signal",
        lambda *_: after,
    )
    monkeypatch.setattr(
        admin_repository,
        "get_source_for_admin",
        lambda *_: source_row("published"),
    )

    admin_content.patch_legal_signal(
        cast(Any, FakeConnection()),
        str(before["id"]),
        LegalSignalPatch(status=PublicationStatus.archived),
        "admin",
    )

    assert audit_events[0]["action"] == "archived"
    assert domain_events == []


def test_source_create_and_patch_write_audit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    audit_events = patch_audit(monkeypatch)
    created = source_row("draft")
    before = source_row("review")
    after = {**before, "title": "Updated source"}
    rows = [before, after]
    monkeypatch.setattr(
        admin_repository,
        "get_country_id_by_slug",
        lambda *_: str(uuid4()),
    )
    monkeypatch.setattr(admin_repository, "create_source", lambda *_: created)
    monkeypatch.setattr(
        admin_repository,
        "get_source_for_admin",
        lambda *_: rows.pop(0),
    )
    monkeypatch.setattr(admin_repository, "patch_source", lambda *_: after)

    admin_content.create_source(
        cast(Any, FakeConnection()),
        SourceCreate(country_slug="argentina", title="Source"),
        "admin",
    )
    admin_content.patch_source(
        cast(Any, FakeConnection()),
        str(before["id"]),
        SourcePatch(title="Updated source"),
        "admin",
    )

    assert [event["action"] for event in audit_events] == ["created", "updated"]
    assert audit_events[1]["changes"]["title"]["new"] == "Updated source"


def test_evidence_create_and_patch_write_audit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    audit_events = patch_audit(monkeypatch)
    created = evidence_row("draft")
    before = evidence_row("review")
    after = {**before, "claim": "Updated claim"}
    rows = [before, after]
    monkeypatch.setattr(
        admin_repository,
        "get_country_id_by_slug",
        lambda *_: str(uuid4()),
    )
    monkeypatch.setattr(
        admin_repository, "get_source_for_admin", lambda *_: None
    )
    monkeypatch.setattr(
        admin_repository, "get_legal_signal_for_admin", lambda *_: None
    )
    monkeypatch.setattr(
        admin_repository, "create_evidence_item", lambda *_: created
    )
    monkeypatch.setattr(
        admin_repository,
        "get_evidence_item_for_admin",
        lambda *_: rows.pop(0),
    )
    monkeypatch.setattr(
        admin_repository, "patch_evidence_item", lambda *_: after
    )

    admin_content.create_evidence_item(
        cast(Any, FakeConnection()),
        EvidenceItemCreate(country_slug="argentina", claim="Claim"),
        "admin",
    )
    admin_content.patch_evidence_item(
        cast(Any, FakeConnection()),
        str(before["id"]),
        EvidenceItemPatch(claim="Updated claim"),
        "admin",
    )

    assert [event["action"] for event in audit_events] == ["created", "updated"]
    assert audit_events[1]["changes"]["claim"]["new"] == "Updated claim"


def test_country_profile_patch_writes_audit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = country_profile_row("review")
    after = {**before, "executive_summary": "Updated summary"}
    rows = [before, after]
    audit_events = patch_audit(monkeypatch)
    monkeypatch.setattr(
        admin_repository,
        "get_country_profile_for_admin",
        lambda *_: rows.pop(0),
    )
    monkeypatch.setattr(
        admin_repository,
        "patch_country_profile",
        lambda *_: after,
    )

    admin_content.patch_country_profile(
        cast(Any, FakeConnection()),
        "argentina",
        CountryProfilePatch(executive_summary="Updated summary"),
        "admin",
    )

    assert audit_events[0]["entity_type"] == "country_profile"
    assert (
        audit_events[0]["changes"]["executive_summary"]["new"]
        == "Updated summary"
    )


def test_publish_validation_still_blocks_invalid_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = legal_signal_row("review", source_id=None)
    monkeypatch.setattr(
        admin_repository,
        "get_legal_signal_for_admin",
        lambda *_: before,
    )

    with pytest.raises(HTTPException) as exc:
        admin_content.patch_legal_signal(
            cast(Any, FakeConnection()),
            str(before["id"]),
            LegalSignalPatch(status=PublicationStatus.published),
            "admin",
        )

    assert exc.value.status_code == 422
    detail = cast(dict[str, Any], exc.value.detail)
    assert detail["error"]["code"] == "data_quality_validation_failed"


def test_publishing_a_source_upserts_both_locale_search_documents(
    monkeypatch: pytest.MonkeyPatch,
    stub_search_index: dict[str, list[dict[str, Any]]],
) -> None:
    before = source_row("review")
    after = {**before, "status": "published"}
    rows = [before, after]
    patch_audit(monkeypatch)
    monkeypatch.setattr(
        admin_repository, "get_source_for_admin", lambda *_: rows.pop(0)
    )
    monkeypatch.setattr(admin_repository, "patch_source", lambda *_: after)

    admin_content.patch_source(
        cast(Any, FakeConnection()),
        str(before["id"]),
        SourcePatch(status=PublicationStatus.published),
        "admin",
    )

    upserted = stub_search_index["upsert"]
    assert stub_search_index["delete"] == []
    assert {call["locale"] for call in upserted} == {"en", "ru"}
    assert all(call["entity_type"] == "source" for call in upserted)
    assert all(
        call["path"] == "/sources?country_slug=argentina" for call in upserted
    )


def test_unpublishing_a_source_removes_both_locale_search_documents(
    monkeypatch: pytest.MonkeyPatch,
    stub_search_index: dict[str, list[dict[str, Any]]],
) -> None:
    before = source_row("published")
    after = {**before, "status": "archived"}
    rows = [before, after]
    patch_audit(monkeypatch)
    monkeypatch.setattr(
        admin_repository, "get_source_for_admin", lambda *_: rows.pop(0)
    )
    monkeypatch.setattr(admin_repository, "patch_source", lambda *_: after)

    admin_content.patch_source(
        cast(Any, FakeConnection()),
        str(before["id"]),
        SourcePatch(status=PublicationStatus.archived),
        "admin",
    )

    assert stub_search_index["upsert"] == []
    deleted = stub_search_index["delete"]
    assert {call["locale"] for call in deleted} == {"en", "ru"}
    assert all(call["entity_type"] == "source" for call in deleted)


def test_publishing_a_legal_signal_upserts_distinct_content_per_locale(
    monkeypatch: pytest.MonkeyPatch,
    stub_search_index: dict[str, list[dict[str, Any]]],
) -> None:
    before = legal_signal_row("review")
    after = {**before, "status": "published"}
    rows = [before, after]
    patch_audit(monkeypatch)
    patch_domain_events(monkeypatch)
    monkeypatch.setattr(
        admin_repository, "get_legal_signal_for_admin", lambda *_: rows.pop(0)
    )
    monkeypatch.setattr(
        admin_repository, "patch_legal_signal", lambda *_: after
    )
    monkeypatch.setattr(
        admin_repository,
        "get_source_for_admin",
        lambda *_: source_row("published"),
    )

    admin_content.patch_legal_signal(
        cast(Any, FakeConnection()),
        str(before["id"]),
        LegalSignalPatch(status=PublicationStatus.published),
        "admin",
    )

    upserted = {call["locale"]: call for call in stub_search_index["upsert"]}
    assert upserted["en"]["title"] == before["title_en"]
    assert upserted["ru"]["title"] == before["title_ru"]
    assert upserted["en"]["path"] == "/legal-signals?country_slug=argentina"


def test_publishing_a_country_profile_upserts_one_locale_document(
    monkeypatch: pytest.MonkeyPatch,
    stub_search_index: dict[str, list[dict[str, Any]]],
) -> None:
    before = country_profile_row("review")
    after = {**before, "status": "published"}
    rows = [before, after]
    patch_audit(monkeypatch)
    monkeypatch.setattr(
        admin_repository,
        "get_country_profile_for_admin",
        lambda *_: rows.pop(0),
    )
    monkeypatch.setattr(
        admin_repository, "patch_country_profile", lambda *_: after
    )

    admin_content.patch_country_profile(
        cast(Any, FakeConnection()),
        "argentina",
        CountryProfilePatch(status=PublicationStatus.published),
        "admin",
    )

    upserted = stub_search_index["upsert"]
    assert len(upserted) == 1
    assert upserted[0]["entity_type"] == "country"
    assert upserted[0]["title"] == "Argentina"
    assert upserted[0]["path"] == "/countries/argentina"
    assert upserted[0]["locale"] == "en"
