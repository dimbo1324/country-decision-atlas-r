from app.core.config import Settings
from app.core.errors import api_error
from app.repositories import contradiction_candidates as repository
from app.repositories.domain_events import insert_domain_event
from app.services.ai_context import build_ask_context
from psycopg import Connection
from typing import Any


def detect_contradiction_candidate(
    connection: Connection[Any],
    settings: Settings,
    *,
    country_slug: str | None,
    topic: str,
    entity_type: str | None,
    entity_id: str | None,
    locale: str,
) -> dict[str, Any]:
    package = build_ask_context(
        connection,
        settings,
        question=topic,
        locale=locale,
        types=None,
        country_slug=country_slug,
        route_id=None,
        route_slug=None,
    )
    items = package.grounded_context
    if package.refusal_reason is not None or len(items) < 2:
        raise api_error(
            422,
            "contradiction_candidate_insufficient_context",
            "Not enough published context items to detect a contradiction candidate.",
        )
    claim_a = items[0].excerpt[:500] or items[0].title
    claim_b = items[1].excerpt[:500] or items[1].title
    source_ids = _unique(
        [citation.source_id for citation in package.citations if citation.source_id]
    )
    evidence_item_ids = _unique(
        [
            citation.evidence_item_id
            for citation in package.citations
            if citation.evidence_item_id
        ]
    )
    summary = f"[FAKE AI] Possible contradiction detected for '{topic}' between {len(items)} published context items."
    row = repository.insert_contradiction_candidate(
        connection,
        country_slug=country_slug,
        topic=topic,
        entity_type=entity_type,
        entity_id=entity_id,
        severity="medium",
        summary=summary,
        claim_a=claim_a,
        claim_b=claim_b,
        source_ids=source_ids,
        evidence_item_ids=evidence_item_ids,
        detected_by="fake_ai",
        provider=settings.ai_provider,
        model_name=settings.ai_model,
        model_version=settings.ai_model_version,
        confidence="low",
    )
    _emit_contradiction_candidate_created_event(connection, row)
    return row


def list_contradiction_candidates_for_admin(
    connection: Connection[Any],
    *,
    status: str | None = None,
    severity: str | None = None,
    limit: int = 50,
) -> tuple[list[dict[str, Any]], int]:
    items = repository.list_contradiction_candidates(
        connection, status=status, severity=severity, limit=limit
    )
    total = repository.count_contradiction_candidates(connection, status=status)
    return items, total


def get_contradiction_candidate_for_admin(
    connection: Connection[Any], candidate_id: str
) -> dict[str, Any]:
    row = repository.get_contradiction_candidate(connection, candidate_id)
    if row is None:
        raise api_error(
            404,
            "contradiction_candidate_not_found",
            f"Contradiction candidate not found: {candidate_id}",
        )
    return row


def update_contradiction_candidate_status(
    connection: Connection[Any],
    candidate_id: str,
    status: str,
    reviewed_by: str | None,
) -> dict[str, Any]:
    row = repository.update_contradiction_candidate_status(
        connection, candidate_id, status, reviewed_by=reviewed_by
    )
    if row is None:
        raise api_error(
            404,
            "contradiction_candidate_not_found",
            f"Contradiction candidate not found: {candidate_id}",
        )
    return row


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _emit_contradiction_candidate_created_event(
    connection: Connection[Any], candidate: dict[str, Any]
) -> None:
    insert_domain_event(
        connection,
        event_key=f"contradiction_candidate:{candidate['id']}:contradiction_candidate.created",
        event_type="contradiction_candidate.created",
        aggregate_type="contradiction_candidate",
        aggregate_id=candidate["id"],
        country_slug=candidate.get("country_slug"),
        payload={
            "topic": candidate["topic"],
            "severity": candidate["severity"],
            "status": candidate["status"],
        },
        status="pending",
        notifiable=False,
    )
