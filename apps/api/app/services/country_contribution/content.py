import json
from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import (
    admin_content as admin_content_repository,
    country_contribution as repository,
)
from app.schemas.admin_content import (
    EvidenceItemCreate,
    EvidenceItemPatch,
    LegalSignalCreate,
    LegalSignalPatch,
    SourceCreate,
    SourcePatch,
)
from app.schemas.common import PublicationStatus
from app.services import admin_content
from app.services.country_contribution import helpers
from psycopg import Connection
from typing import Any


def _draft_owner_proposal(
    connection: Connection[Any], *, proposal_id: str, current_user: CurrentUser
) -> dict[str, Any]:
    proposal = helpers.get_owner_proposal_or_404(
        connection, proposal_id, current_user.id
    )
    helpers.require_draft_editable(proposal)
    return proposal


def _ensure_same_country(proposal: dict[str, Any], country_id: Any) -> None:
    if str(country_id) != str(proposal["country_id"]):
        raise api_error(
            403,
            "country_proposal_scope_violation",
            "You can only edit content that belongs to your own country proposal.",
            {},
        )


def create_my_source(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    payload: Any,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = _draft_owner_proposal(
        connection, proposal_id=proposal_id, current_user=current_user
    )
    source_payload = SourceCreate(
        country_slug=proposal["slug"],
        title=payload.title,
        url=payload.url,
        source_type=payload.source_type,
        publisher=payload.publisher,
        language=payload.language,
        confidence=payload.confidence,
        published_at=payload.published_at,
        last_checked_at=payload.last_checked_at,
        notes=payload.notes,
        status=PublicationStatus.draft,
    )
    return admin_content.create_source(
        connection, source_payload, current_user.email
    )


def patch_my_source(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    source_id: str,
    payload: Any,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = _draft_owner_proposal(
        connection, proposal_id=proposal_id, current_user=current_user
    )
    existing = admin_content_repository.get_source_for_admin(
        connection, source_id
    )
    if existing is None:
        raise api_error(404, "source_not_found", "Source was not found.", {})
    _ensure_same_country(proposal, existing["country_id"])
    patch_payload = SourcePatch(**payload.model_dump(exclude_unset=True))
    return admin_content.patch_source(
        connection, source_id, patch_payload, current_user.email
    )


def create_my_evidence_item(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    payload: Any,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = _draft_owner_proposal(
        connection, proposal_id=proposal_id, current_user=current_user
    )
    evidence_payload = EvidenceItemCreate(
        country_slug=proposal["slug"],
        source_id=payload.source_id,
        legal_signal_id=payload.legal_signal_id,
        claim=payload.claim,
        excerpt=payload.excerpt,
        url=payload.url,
        confidence=payload.confidence,
        status=PublicationStatus.draft,
    )
    return admin_content.create_evidence_item(
        connection, evidence_payload, current_user.email
    )


def patch_my_evidence_item(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    evidence_item_id: str,
    payload: Any,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = _draft_owner_proposal(
        connection, proposal_id=proposal_id, current_user=current_user
    )
    existing = admin_content_repository.get_evidence_item_for_admin(
        connection, evidence_item_id
    )
    if existing is None:
        raise api_error(
            404, "evidence_item_not_found", "Evidence item was not found.", {}
        )
    _ensure_same_country(proposal, existing["country_id"])
    patch_payload = EvidenceItemPatch(**payload.model_dump(exclude_unset=True))
    return admin_content.patch_evidence_item(
        connection, evidence_item_id, patch_payload, current_user.email
    )


def create_my_legal_signal(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    payload: Any,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = _draft_owner_proposal(
        connection, proposal_id=proposal_id, current_user=current_user
    )
    signal_payload = LegalSignalCreate(
        country_slug=proposal["slug"],
        source_id=payload.source_id,
        title_en=payload.title_en,
        title_ru=payload.title_ru,
        summary_en=payload.summary_en,
        summary_ru=payload.summary_ru,
        signal_type=payload.signal_type,
        impact_direction=payload.impact_direction,
        impact_level=payload.impact_level,
        legal_status=payload.legal_status,
        affected_groups=payload.affected_groups,
        published_date=payload.published_date,
        effective_date=payload.effective_date,
        confidence=payload.confidence,
        status=PublicationStatus.draft,
    )
    return admin_content.create_legal_signal(
        connection, signal_payload, current_user.email
    )


def patch_my_legal_signal(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    signal_id: str,
    payload: Any,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = _draft_owner_proposal(
        connection, proposal_id=proposal_id, current_user=current_user
    )
    existing = admin_content_repository.get_legal_signal_for_admin(
        connection, signal_id
    )
    if existing is None:
        raise api_error(
            404, "legal_signal_not_found", "Legal signal was not found.", {}
        )
    _ensure_same_country(proposal, existing["country_id"])
    patch_payload = LegalSignalPatch(**payload.model_dump(exclude_unset=True))
    return admin_content.patch_legal_signal(
        connection, signal_id, patch_payload, current_user.email
    )


def create_my_timeline_event(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    payload: Any,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = _draft_owner_proposal(
        connection, proposal_id=proposal_id, current_user=current_user
    )
    signal_country_id = repository.get_legal_signal_country_id(
        connection, str(payload.legal_signal_id)
    )
    if signal_country_id is None:
        raise api_error(
            404, "legal_signal_not_found", "Legal signal was not found.", {}
        )
    _ensure_same_country(proposal, signal_country_id)
    if payload.source_id is None and payload.evidence_item_id is None:
        raise api_error(
            422,
            "timeline_event_source_required",
            "Timeline event needs a source or an evidence item.",
            {},
        )
    if payload.source_id is not None and not repository.source_exists(
        connection, str(payload.source_id)
    ):
        raise api_error(404, "source_not_found", "Source was not found.", {})
    if (
        payload.evidence_item_id is not None
        and not repository.evidence_item_exists(
            connection, str(payload.evidence_item_id)
        )
    ):
        raise api_error(
            404, "evidence_item_not_found", "Evidence item was not found.", {}
        )
    return repository.create_timeline_event(
        connection,
        country_id=proposal["country_id"],
        data={
            "legal_signal_id": str(payload.legal_signal_id),
            "event_date": payload.event_date,
            "event_type": payload.event_type,
            "impact_direction": payload.impact_direction,
            "impact_level": payload.impact_level,
            "title": payload.title,
            "summary": payload.summary,
            "source_id": str(payload.source_id) if payload.source_id else None,
            "evidence_item_id": (
                str(payload.evidence_item_id)
                if payload.evidence_item_id
                else None
            ),
            "affected_groups": _json_list(payload.affected_groups),
        },
    )


def upsert_my_card(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    locale: str,
    payload: Any,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = _draft_owner_proposal(
        connection, proposal_id=proposal_id, current_user=current_user
    )
    if locale not in {"en", "ru"}:
        raise api_error(
            422, "invalid_locale", "Locale must be 'en' or 'ru'.", {}
        )
    return repository.upsert_card(
        connection,
        country_id=proposal["country_id"],
        locale=locale,
        fields=payload.model_dump(),
    )


def upsert_my_metric_values(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    entries: list[Any],
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = _draft_owner_proposal(
        connection, proposal_id=proposal_id, current_user=current_user
    )
    slugs = [entry.metric_slug for entry in entries]
    if len(slugs) != len(set(slugs)):
        raise api_error(
            422,
            "duplicate_metric_slug",
            "Duplicate metric_slug values are not allowed in a single request.",
            {},
        )
    metric_ids: dict[str, str] = {}
    for slug in slugs:
        metric_id = repository.get_cii_metric_id_by_slug(connection, slug)
        if metric_id is None:
            raise api_error(
                404,
                "cii_metric_not_found",
                "CII metric definition was not found.",
                {"metric_slug": slug},
            )
        metric_ids[slug] = metric_id
    results = []
    with connection.transaction():
        for entry in entries:
            row = repository.upsert_metric_value(
                connection,
                country_id=proposal["country_id"],
                metric_id=metric_ids[entry.metric_slug],
                raw_value=float(entry.raw_value),
                normalized_value=float(entry.normalized_value),
                data_year=entry.data_year,
                source_name=entry.source_name,
                source_url=entry.source_url,
                reliability=entry.reliability,
            )
            results.append(row)
    return {"items": results, "total": len(results)}


def _json_list(values: list[str]) -> str:
    return json.dumps(list(values))
