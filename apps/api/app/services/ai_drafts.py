from app.core.config import Settings
from app.core.errors import api_error
from app.repositories import ai_drafts as repository
from app.repositories.domain_events import insert_domain_event
from app.services.ai_context import build_ask_context
from psycopg import Connection
from typing import Any


def generate_summary_draft(
    connection: Connection[Any],
    settings: Settings,
    *,
    country_slug: str | None,
    route_id: str | None,
    source_id: str | None,
    evidence_item_id: str | None,
    topic: str,
    locale: str,
) -> dict[str, Any]:
    package = build_ask_context(
        connection,
        settings,
        question=topic,
        locale=locale,
        types=None,
        country_slug=country_slug,
        route_id=route_id,
        route_slug=None,
    )
    if package.refusal_reason is not None or not package.citations:
        raise api_error(
            422,
            "ai_draft_insufficient_context",
            "Not enough published context to generate an AI draft.",
        )
    body_lines = [
        item.excerpt[:400] for item in package.grounded_context if item.excerpt
    ]
    body = "\n".join(body_lines) if body_lines else package.grounded_context[0].title
    summary = f"[FAKE AI] Summary draft for '{topic}' based on {len(package.grounded_context)} published context items."
    citations = [citation.model_dump() for citation in package.citations]
    row = repository.insert_ai_draft(
        connection,
        draft_type="summary",
        country_slug=country_slug,
        route_id=route_id,
        legal_signal_id=None,
        source_id=source_id,
        evidence_item_id=evidence_item_id,
        title=f"Summary draft: {topic}"[:250],
        body=body,
        summary=summary,
        detected_issue=None,
        provider=settings.ai_provider,
        model_name=settings.ai_model,
        model_version="v1",
        input_context={"topic": topic, "locale": locale},
        citations=citations,
        confidence="medium" if len(citations) > 1 else "low",
    )
    _emit_ai_draft_ready_event(connection, row)
    return row


def list_ai_drafts_for_admin(
    connection: Connection[Any],
    *,
    status: str | None = None,
    draft_type: str | None = None,
    limit: int = 50,
) -> tuple[list[dict[str, Any]], int]:
    items = repository.list_ai_drafts(
        connection, status=status, draft_type=draft_type, limit=limit
    )
    total = repository.count_ai_drafts(connection, status=status)
    return items, total


def get_ai_draft_for_admin(
    connection: Connection[Any], draft_id: str
) -> dict[str, Any]:
    row = repository.get_ai_draft(connection, draft_id)
    if row is None:
        raise api_error(404, "ai_draft_not_found", f"AI draft not found: {draft_id}")
    return row


def update_ai_draft_status(
    connection: Connection[Any],
    draft_id: str,
    status: str,
    reviewed_by: str | None,
) -> dict[str, Any]:
    row = repository.update_ai_draft_status(
        connection, draft_id, status, reviewed_by=reviewed_by
    )
    if row is None:
        raise api_error(404, "ai_draft_not_found", f"AI draft not found: {draft_id}")
    return row


def _emit_ai_draft_ready_event(
    connection: Connection[Any], draft: dict[str, Any]
) -> None:
    insert_domain_event(
        connection,
        event_key=f"ai_draft:{draft['id']}:ai_draft.ready",
        event_type="ai_draft.ready",
        aggregate_type="ai_draft",
        aggregate_id=draft["id"],
        country_slug=draft.get("country_slug"),
        payload={
            "draft_type": draft["draft_type"],
            "status": draft["status"],
            "title": draft["title"],
        },
        status="pending",
        notifiable=False,
    )
