"""AI draft generation service: refusal without context, draft creation, and status updates."""

from app.core.config import Settings
from app.repositories import ai_drafts as repository
from app.schemas.ai import AICitation, AIContextItem
from app.services import ai_drafts as service
from app.services.ai_context import AIContextPackage
from fastapi import HTTPException
from psycopg import Connection
import pytest
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def _context_item() -> AIContextItem:
    return AIContextItem(
        entity_type="source",
        entity_id="source-1",
        country_slug="uruguay",
        title="Residence law",
        excerpt="Published excerpt about the residence process.",
        url_path="/sources/source-1",
        source_ids=["source-1"],
        confidence="high",
        freshness_status="fresh",
    )


def _citation() -> AICitation:
    return AICitation(
        entity_type="source",
        entity_id="source-1",
        title="Residence law",
        source_id="source-1",
        country_slug="uruguay",
    )


def _grounded_package() -> AIContextPackage:
    return AIContextPackage(
        system_rules=[],
        user_question="residence",
        grounded_context=[_context_item()],
        citations=[_citation()],
        citation_policy="cite",
        disclaimer_policy="disclaimer",
        locale="ru",
        refusal_reason=None,
    )


def _refused_package() -> AIContextPackage:
    return AIContextPackage(
        system_rules=[],
        user_question="residence",
        grounded_context=[],
        citations=[],
        citation_policy="cite",
        disclaimer_policy="disclaimer",
        locale="ru",
        refusal_reason="insufficient",
    )


def test_generate_summary_draft_refuses_without_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        service, "build_ask_context", lambda *_a, **_kw: _refused_package()
    )

    with pytest.raises(HTTPException) as exc_info:
        service.generate_summary_draft(
            CONNECTION,
            Settings(app_env="local"),
            country_slug="uruguay",
            route_id=None,
            source_id=None,
            evidence_item_id=None,
            topic="residence",
            locale="ru",
        )
    assert exc_info.value.status_code == 422


def test_generate_summary_draft_creates_needs_review_draft_with_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        service, "build_ask_context", lambda *_a, **_kw: _grounded_package()
    )
    inserted: dict[str, Any] = {}
    events: dict[str, Any] = {}

    def fake_insert(_conn: Any, **kwargs: Any) -> dict[str, Any]:
        inserted.update(kwargs)
        return {
            "id": "draft-1",
            "draft_type": "summary",
            "status": "needs_review",
            "country_slug": kwargs["country_slug"],
            "title": kwargs["title"],
        }

    def fake_event(_conn: Any, **kwargs: Any) -> None:
        events.update(kwargs)

    monkeypatch.setattr(repository, "insert_ai_draft", fake_insert)
    monkeypatch.setattr(service, "insert_domain_event", fake_event)

    row = service.generate_summary_draft(
        CONNECTION,
        Settings(app_env="local", ai_model_version="test-v2"),
        country_slug="uruguay",
        route_id=None,
        source_id=None,
        evidence_item_id=None,
        topic="residence",
        locale="ru",
    )

    assert row["status"] == "needs_review"
    assert inserted["citations"]
    assert inserted["model_version"] == "test-v2"
    assert events["event_type"] == "ai_draft.ready"
    assert events["notifiable"] is False


def test_update_ai_draft_status_not_found_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "update_ai_draft_status", lambda *_a, **_kw: None)

    with pytest.raises(HTTPException) as exc_info:
        service.update_ai_draft_status(CONNECTION, "missing", "approved", "editor")
    assert exc_info.value.status_code == 404


def test_approved_status_does_not_touch_public_read_model() -> None:
    source_names = dir(service)
    assert "publish_to_read_model" not in source_names
    assert "publish" not in source_names
