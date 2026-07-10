from app.core.errors import api_error
from app.repositories import admin_content as repository
from app.repositories.audit import insert_audit_event
from app.repositories.domain_events import insert_domain_event
from app.schemas.admin_content import (
    CountryProfilePatch,
    EvidenceItemCreate,
    EvidenceItemPatch,
    LegalSignalCreate,
    LegalSignalPatch,
    SourceCreate,
    SourcePatch,
    UserStoryAdminCreate,
    UserStoryPatch,
)
from app.schemas.common import PublicationStatus
from app.services import search_index
from app.services.cache_invalidation import (
    invalidate_country_cache,
    invalidate_home_cache,
    invalidate_legal_timeline_cache,
)
from app.services.data_quality import (
    raise_if_critical_issues,
    validate_country_card_for_publish,
    validate_evidence_item_for_publish,
    validate_legal_signal_for_publish,
    validate_source_for_publish,
    validate_user_story_for_publish,
)
from app.services.publication import (
    audit_action_for_transition,
    ensure_allowed_transition,
    is_publish_transition,
)
from enum import StrEnum
from psycopg import Connection
from typing import Any
from uuid import UUID


SOURCE_AUDIT_FIELDS = (
    "country_id",
    "title",
    "url",
    "source_type",
    "publisher",
    "language",
    "confidence",
    "published_at",
    "last_checked_at",
    "notes",
    "status",
)
EVIDENCE_AUDIT_FIELDS = (
    "source_id",
    "country_id",
    "legal_signal_id",
    "claim",
    "excerpt",
    "url",
    "confidence",
    "status",
)
LEGAL_SIGNAL_AUDIT_FIELDS = (
    "country_id",
    "source_id",
    "title_en",
    "title_ru",
    "summary_en",
    "summary_ru",
    "signal_type",
    "impact_direction",
    "impact_level",
    "legal_status",
    "affected_groups",
    "published_date",
    "effective_date",
    "confidence",
    "status",
)
COUNTRY_PROFILE_AUDIT_FIELDS = (
    "locale",
    "executive_summary",
    "migration_overview",
    "tax_overview",
    "cost_of_living_overview",
    "business_overview",
    "safety_overview",
    "legal_signals_summary",
    "risk_summary",
    "source_summary",
    "status",
)
USER_STORY_AUDIT_FIELDS = (
    "origin_country_id",
    "destination_country_id",
    "city",
    "year",
    "scenario",
    "budget_initial_usd",
    "budget_monthly_usd",
    "legal_path",
    "documents_used",
    "problems",
    "positive_outcome",
    "negative_outcome",
    "advice",
    "satisfaction_score",
    "verification_status",
    "status",
    "is_synthetic",
    "notes",
)


def create_source(
    connection: Connection[Any],
    payload: SourceCreate,
    changed_by: str,
) -> dict[str, Any]:
    data = _model_data(payload)
    data["country_id"] = _country_id_or_none(
        connection, data.pop("country_slug", None)
    )
    if data.get("status") == PublicationStatus.published.value:
        raise_if_critical_issues(validate_source_for_publish(data))
    with connection.transaction():
        row = repository.create_source(connection, data)
        _audit_create(connection, "source", row, changed_by)
        _sync_single_locale_both_index(
            connection,
            "source",
            row,
            title=str(row.get("title") or ""),
            summary=str(row.get("publisher") or ""),
        )
    return row


def patch_source(
    connection: Connection[Any],
    source_id: str,
    payload: SourcePatch,
    changed_by: str,
) -> dict[str, Any]:
    with connection.transaction():
        before = _require(
            repository.get_source_for_admin(connection, source_id), "Source"
        )
        data = _model_data(payload, exclude_unset=True)
        _ensure_status_transition(before, data)
        candidate = {**before, **data}
        if candidate.get("status") == PublicationStatus.published.value:
            raise_if_critical_issues(validate_source_for_publish(candidate))
        repository.patch_source(connection, source_id, data)
        after = _require(
            repository.get_source_for_admin(connection, source_id), "Source"
        )
        _audit_patch(
            connection,
            "source",
            before,
            after,
            changed_by,
            SOURCE_AUDIT_FIELDS,
        )
        _sync_single_locale_both_index(
            connection,
            "source",
            after,
            title=str(after.get("title") or ""),
            summary=str(after.get("publisher") or ""),
        )
    return after


def create_evidence_item(
    connection: Connection[Any],
    payload: EvidenceItemCreate,
    changed_by: str,
) -> dict[str, Any]:
    data = _model_data(payload)
    data["country_id"] = _country_id_or_none(
        connection, data.pop("country_slug", None)
    )
    _validate_source_exists(connection, data.get("source_id"))
    _validate_legal_signal_exists(connection, data.get("legal_signal_id"))
    if data.get("status") == PublicationStatus.published.value:
        raise_if_critical_issues(validate_evidence_item_for_publish(data))
    with connection.transaction():
        row = repository.create_evidence_item(connection, data)
        _audit_create(connection, "evidence_item", row, changed_by)
        _sync_single_locale_both_index(
            connection,
            "evidence_item",
            row,
            title=str(row.get("title") or ""),
            summary=str(row.get("summary") or ""),
        )
    return row


def patch_evidence_item(
    connection: Connection[Any],
    evidence_item_id: str,
    payload: EvidenceItemPatch,
    changed_by: str,
) -> dict[str, Any]:
    with connection.transaction():
        before = _require(
            repository.get_evidence_item_for_admin(
                connection, evidence_item_id
            ),
            "Evidence item",
        )
        data = _model_data(payload, exclude_unset=True)
        _validate_source_exists(connection, data.get("source_id"))
        _validate_legal_signal_exists(connection, data.get("legal_signal_id"))
        _ensure_status_transition(before, data)
        candidate = {**before, **data}
        if candidate.get("status") == PublicationStatus.published.value:
            raise_if_critical_issues(
                validate_evidence_item_for_publish(candidate)
            )
        repository.patch_evidence_item(connection, evidence_item_id, data)
        after = _require(
            repository.get_evidence_item_for_admin(
                connection, evidence_item_id
            ),
            "Evidence item",
        )
        _audit_patch(
            connection,
            "evidence_item",
            before,
            after,
            changed_by,
            EVIDENCE_AUDIT_FIELDS,
        )
        _sync_single_locale_both_index(
            connection,
            "evidence_item",
            after,
            title=str(after.get("title") or ""),
            summary=str(after.get("summary") or ""),
        )
    return after


def create_legal_signal(
    connection: Connection[Any],
    payload: LegalSignalCreate,
    changed_by: str,
) -> dict[str, Any]:
    data = _model_data(payload)
    data["country_id"] = _country_id_required(
        connection, data.pop("country_slug")
    )
    _validate_source_exists(connection, data.get("source_id"))
    if data.get("status") == PublicationStatus.published.value:
        raise_if_critical_issues(validate_legal_signal_for_publish(data))
    with connection.transaction():
        row = repository.create_legal_signal(connection, data)
        _audit_create(connection, "legal_signal", row, changed_by)
        _sync_legal_signal_index(connection, row)
    return row


def patch_legal_signal(
    connection: Connection[Any],
    signal_id: str,
    payload: LegalSignalPatch,
    changed_by: str,
) -> dict[str, Any]:
    with connection.transaction():
        before = _require(
            repository.get_legal_signal_for_admin(connection, signal_id),
            "Legal signal",
        )
        data = _model_data(payload, exclude_unset=True)
        _validate_source_exists(connection, data.get("source_id"))
        _ensure_status_transition(before, data)
        candidate = {**before, **data}
        if candidate.get("status") == PublicationStatus.published.value:
            raise_if_critical_issues(
                validate_legal_signal_for_publish(candidate)
            )
        repository.patch_legal_signal(connection, signal_id, data)
        after = _require(
            repository.get_legal_signal_for_admin(connection, signal_id),
            "Legal signal",
        )
        _audit_patch(
            connection,
            "legal_signal",
            before,
            after,
            changed_by,
            LEGAL_SIGNAL_AUDIT_FIELDS,
        )
        _sync_legal_signal_index(connection, after)
        _emit_legal_signal_published_event(connection, before, after)
    if is_publish_transition(
        str(before.get("status")), str(after.get("status"))
    ):
        country_slug = repository.get_country_slug_by_id(
            connection, str(after["country_id"])
        )
        if country_slug:
            invalidate_legal_timeline_cache(country_slug)
            invalidate_country_cache(country_slug)
            invalidate_home_cache()
    return after


def patch_country_profile(
    connection: Connection[Any],
    country_slug: str,
    payload: CountryProfilePatch,
    changed_by: str,
) -> dict[str, Any]:
    with connection.transaction():
        data = _model_data(payload, exclude_unset=True)
        before = _require(
            repository.get_country_profile_for_admin(
                connection, country_slug, data.get("locale", "en")
            ),
            "Country profile",
        )
        _ensure_status_transition(before, data)
        candidate = {**before, **data}
        if candidate.get("status") == PublicationStatus.published.value:
            raise_if_critical_issues(
                validate_country_card_for_publish(candidate)
            )
        repository.patch_country_profile(connection, country_slug, data)
        after = _require(
            repository.get_country_profile_for_admin(
                connection,
                country_slug,
                data.get("locale", before.get("locale", "en")),
            ),
            "Country profile",
        )
        _audit_patch(
            connection,
            "country_profile",
            before,
            after,
            changed_by,
            COUNTRY_PROFILE_AUDIT_FIELDS,
        )
        _sync_country_profile_index(connection, after, country_slug)
    country_slug_after = str(after.get("country_slug") or country_slug)
    invalidate_country_cache(country_slug_after)
    invalidate_home_cache()
    return after


def create_user_story(
    connection: Connection[Any],
    payload: UserStoryAdminCreate,
    changed_by: str,
) -> dict[str, Any]:
    data = _model_data(payload)
    data["origin_country_id"] = _country_id_or_none(
        connection, data.pop("origin_country_slug", None)
    )
    data["destination_country_id"] = _country_id_required(
        connection, data.pop("destination_country_slug")
    )
    if data.get("status") == PublicationStatus.published.value:
        raise_if_critical_issues(validate_user_story_for_publish(data))
    with connection.transaction():
        row = repository.create_user_story_for_admin(connection, data)
        _audit_create(connection, "user_story", row, changed_by)
    return row


def patch_user_story(
    connection: Connection[Any],
    story_id: str,
    payload: UserStoryPatch,
    changed_by: str,
) -> dict[str, Any]:
    with connection.transaction():
        before = _require(
            repository.get_user_story_for_admin(connection, story_id),
            "User story",
        )
        data = _model_data(payload, exclude_unset=True)
        if "origin_country_slug" in data:
            data["origin_country_id"] = _country_id_or_none(
                connection, data.pop("origin_country_slug")
            )
        if "destination_country_slug" in data:
            data["destination_country_id"] = _country_id_required(
                connection, data.pop("destination_country_slug")
            )
        _ensure_status_transition(before, data)
        candidate = {**before, **data}
        if candidate.get("status") == PublicationStatus.published.value:
            raise_if_critical_issues(validate_user_story_for_publish(candidate))
        repository.patch_user_story_for_admin(connection, story_id, data)
        after = _require(
            repository.get_user_story_for_admin(connection, story_id),
            "User story",
        )
        _audit_patch(
            connection,
            "user_story",
            before,
            after,
            changed_by,
            USER_STORY_AUDIT_FIELDS,
        )
    return after


def build_changes(
    old_row: dict[str, Any],
    new_row: dict[str, Any],
    fields: tuple[str, ...],
) -> dict[str, dict[str, Any]]:
    changes: dict[str, dict[str, Any]] = {}
    for field in fields:
        old_value = _json_value(old_row.get(field))
        new_value = _json_value(new_row.get(field))
        if old_value != new_value:
            changes[field] = {"old": old_value, "new": new_value}
    return changes


def _model_data(model: Any, exclude_unset: bool = False) -> dict[str, Any]:
    data = model.model_dump(exclude_unset=exclude_unset, mode="json")
    return {
        key: (value.value if isinstance(value, StrEnum) else value)
        for key, value in data.items()
    }


def _country_id_required(connection: Connection[Any], country_slug: str) -> str:
    country_id = repository.get_country_id_by_slug(connection, country_slug)
    if country_id is None:
        raise api_error(
            404,
            "country_not_found",
            "Country not found.",
            {"country_slug": country_slug},
        )
    return country_id


def _country_id_or_none(
    connection: Connection[Any], country_slug: str | None
) -> str | None:
    if country_slug is None:
        return None
    return _country_id_required(connection, country_slug)


def _validate_source_exists(
    connection: Connection[Any], source_id: Any
) -> None:
    if source_id is None:
        return
    if repository.get_source_for_admin(connection, str(source_id)) is None:
        raise api_error(
            404,
            "source_not_found",
            "Source not found.",
            {"source_id": str(source_id)},
        )


def _validate_legal_signal_exists(
    connection: Connection[Any], legal_signal_id: Any
) -> None:
    if legal_signal_id is None:
        return
    if (
        repository.get_legal_signal_for_admin(connection, str(legal_signal_id))
        is None
    ):
        raise api_error(
            404,
            "legal_signal_not_found",
            "Legal signal not found.",
            {"legal_signal_id": str(legal_signal_id)},
        )


def _require(row: dict[str, Any] | None, entity_name: str) -> dict[str, Any]:
    if row is None:
        raise api_error(404, "not_found", f"{entity_name} not found.")
    return row


def _ensure_status_transition(
    before: dict[str, Any], data: dict[str, Any]
) -> tuple[str, str]:
    old_status = str(before.get("status") or "")
    new_status = str(data.get("status") or old_status)
    if old_status != new_status:
        ensure_allowed_transition(old_status, new_status)
    return old_status, new_status


def _audit_create(
    connection: Connection[Any],
    entity_type: str,
    entity: dict[str, Any],
    changed_by: str,
) -> None:
    _audit(
        connection,
        entity_type,
        entity,
        "created",
        changed_by,
        {"created": entity},
    )


def _audit_patch(
    connection: Connection[Any],
    entity_type: str,
    before: dict[str, Any],
    after: dict[str, Any],
    changed_by: str,
    fields: tuple[str, ...],
) -> None:
    changes = build_changes(before, after, fields)
    if not changes:
        return
    _audit(
        connection,
        entity_type,
        after,
        _audit_action(before, after),
        changed_by,
        changes,
    )


def _audit_action(before: dict[str, Any], after: dict[str, Any]) -> str:
    old_status = before.get("status")
    new_status = after.get("status")
    if (
        old_status != new_status
        and old_status is not None
        and new_status is not None
    ):
        return audit_action_for_transition(str(old_status), str(new_status))
    return "updated"


def _audit(
    connection: Connection[Any],
    entity_type: str,
    entity: dict[str, Any],
    action: str,
    changed_by: str,
    changes: dict[str, Any],
) -> None:
    insert_audit_event(
        connection,
        entity_type=entity_type,
        entity_id=_as_uuid(entity["id"]),
        action=action,
        changed_by=changed_by,
        changes=changes,
    )


def _sync_single_locale_both_index(
    connection: Connection[Any],
    entity_type: str,
    row: dict[str, Any],
    *,
    title: str,
    summary: str,
) -> None:
    """Sources and evidence_items are indexed with the same title/summary
    under both locales (see rebuild_search_index.py's _index_single_locale_both)."""
    country_id = row.get("country_id")
    country_slug = (
        repository.get_country_slug_by_id(connection, str(country_id))
        if country_id
        else None
    )
    path = (
        f"/sources?country_slug={country_slug}" if country_slug else "/sources"
    )
    for locale in ("en", "ru"):
        search_index.sync_document(
            connection,
            entity_type=entity_type,
            entity_id=str(row["id"]),
            country_slug=country_slug,
            locale=locale,
            status=str(row.get("status")),
            title=title,
            summary=summary,
            body="",
            path=path,
            source_updated_at=row.get("updated_at"),
        )


def _sync_legal_signal_index(
    connection: Connection[Any], row: dict[str, Any]
) -> None:
    country_slug = repository.get_country_slug_by_id(
        connection, str(row["country_id"])
    )
    if not country_slug:
        return
    path = f"/legal-signals?country_slug={country_slug}"
    title_en = str(row.get("title_en") or row.get("title") or "")
    title_ru = str(
        row.get("title_ru") or row.get("title_en") or row.get("title") or ""
    )
    summary_en = str(row.get("summary_en") or row.get("summary") or "")
    summary_ru = str(
        row.get("summary_ru")
        or row.get("summary_en")
        or row.get("summary")
        or ""
    )
    for locale, title, summary in (
        ("en", title_en, summary_en),
        ("ru", title_ru, summary_ru),
    ):
        search_index.sync_document(
            connection,
            entity_type="legal_signal",
            entity_id=str(row["id"]),
            country_slug=country_slug,
            locale=locale,
            status=str(row.get("status")),
            title=title,
            summary=summary,
            body="",
            path=path,
            source_updated_at=row.get("updated_at"),
        )


def _sync_country_profile_index(
    connection: Connection[Any], row: dict[str, Any], country_slug: str
) -> None:
    country_name = repository.get_country_name_by_id(
        connection, str(row["country_id"])
    )
    if not country_name:
        return
    body = " ".join(
        str(row.get(field) or "")
        for field in (
            "migration_overview",
            "tax_overview",
            "cost_of_living_overview",
            "business_overview",
            "safety_overview",
        )
    ).strip()
    search_index.sync_document(
        connection,
        entity_type="country",
        entity_id=str(row["country_id"]),
        country_slug=country_slug,
        locale=str(row.get("locale") or "en"),
        status=str(row.get("status")),
        title=country_name,
        summary=str(row.get("executive_summary") or ""),
        body=body,
        path=f"/countries/{country_slug}",
        source_updated_at=row.get("updated_at"),
    )


def _emit_legal_signal_published_event(
    connection: Connection[Any],
    before: dict[str, Any],
    after: dict[str, Any],
) -> None:
    if not is_publish_transition(
        str(before.get("status")), str(after.get("status"))
    ):
        return
    signal_id = str(after["id"])
    country_slug = repository.get_country_slug_by_id(
        connection, str(after["country_id"])
    )
    insert_domain_event(
        connection,
        event_key=f"legal_signal:{signal_id}:legal_signal.published",
        event_type="legal_signal.published",
        aggregate_type="legal_signal",
        aggregate_id=_as_uuid(signal_id),
        country_slug=country_slug,
        payload={
            "id": signal_id,
            "country_slug": country_slug,
            "title": after.get("title")
            or after.get("title_en")
            or after.get("title_ru"),
            "signal_type": after.get("signal_type"),
            "impact_direction": after.get("impact_direction"),
            "impact_level": after.get("impact_level"),
            "legal_status": after.get("legal_status", "unknown"),
        },
        status="pending",
        notifiable=True,
    )


def _as_uuid(value: Any) -> UUID:
    return value if isinstance(value, UUID) else UUID(str(value))


def _json_value(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if (
        isinstance(value, list | dict | str | int | float | bool)
        or value is None
    ):
        return value
    return str(value)
