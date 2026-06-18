from app.core.errors import api_error
from app.repositories import admin_content as repository
from app.repositories.audit import create_audit_event
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
from psycopg import Connection
from typing import Any


def create_source(
    connection: Connection[Any],
    payload: SourceCreate,
    changed_by: str,
) -> dict[str, Any]:
    data = _model_data(payload)
    data["country_id"] = _country_id_or_none(connection, data.pop("country_slug", None))
    if data.get("status") == PublicationStatus.published.value:
        _validate_source_for_publish(data)
    row = repository.create_source(connection, data)
    _audit(connection, "source", row, "created", changed_by, {"after": row})
    return row


def patch_source(
    connection: Connection[Any],
    source_id: str,
    payload: SourcePatch,
    changed_by: str,
) -> dict[str, Any]:
    before = _require(repository.get_source_for_admin(connection, source_id), "Source")
    data = _model_data(payload, exclude_unset=True)
    after = _require(repository.patch_source(connection, source_id, data), "Source")
    if after.get("status") == PublicationStatus.published.value:
        _validate_source_for_publish(after)
    _audit(
        connection,
        "source",
        after,
        _audit_action(before, after),
        changed_by,
        _diff(before, after),
    )
    return after


def create_evidence_item(
    connection: Connection[Any],
    payload: EvidenceItemCreate,
    changed_by: str,
) -> dict[str, Any]:
    data = _model_data(payload)
    data["country_id"] = _country_id_or_none(connection, data.pop("country_slug", None))
    _validate_source_exists(connection, data.get("source_id"))
    _validate_legal_signal_exists(connection, data.get("legal_signal_id"))
    if data.get("status") == PublicationStatus.published.value:
        _validate_evidence_for_publish(data)
    row = repository.create_evidence_item(connection, data)
    _audit(connection, "evidence_item", row, "created", changed_by, {"after": row})
    return row


def patch_evidence_item(
    connection: Connection[Any],
    evidence_item_id: str,
    payload: EvidenceItemPatch,
    changed_by: str,
) -> dict[str, Any]:
    before = _require(
        repository.get_evidence_item_for_admin(connection, evidence_item_id),
        "Evidence item",
    )
    data = _model_data(payload, exclude_unset=True)
    _validate_source_exists(connection, data.get("source_id"))
    _validate_legal_signal_exists(connection, data.get("legal_signal_id"))
    after = _require(
        repository.patch_evidence_item(connection, evidence_item_id, data),
        "Evidence item",
    )
    if after.get("status") == PublicationStatus.published.value:
        _validate_evidence_for_publish(after)
    _audit(
        connection,
        "evidence_item",
        after,
        _audit_action(before, after),
        changed_by,
        _diff(before, after),
    )
    return after


def create_legal_signal(
    connection: Connection[Any],
    payload: LegalSignalCreate,
    changed_by: str,
) -> dict[str, Any]:
    data = _model_data(payload)
    data["country_id"] = _country_id_required(connection, data.pop("country_slug"))
    _validate_source_exists(connection, data.get("source_id"))
    if data.get("status") == PublicationStatus.published.value:
        _validate_legal_signal_for_publish(data)
    row = repository.create_legal_signal(connection, data)
    _audit(connection, "legal_signal", row, "created", changed_by, {"after": row})
    return row


def patch_legal_signal(
    connection: Connection[Any],
    signal_id: str,
    payload: LegalSignalPatch,
    changed_by: str,
) -> dict[str, Any]:
    before = _require(
        repository.get_legal_signal_for_admin(connection, signal_id),
        "Legal signal",
    )
    data = _model_data(payload, exclude_unset=True)
    _validate_source_exists(connection, data.get("source_id"))
    after = _require(
        repository.patch_legal_signal(connection, signal_id, data),
        "Legal signal",
    )
    if after.get("status") == PublicationStatus.published.value:
        _validate_legal_signal_for_publish(after)
    _audit(
        connection,
        "legal_signal",
        after,
        _audit_action(before, after),
        changed_by,
        _diff(before, after),
    )
    return after


def patch_country_profile(
    connection: Connection[Any],
    country_slug: str,
    payload: CountryProfilePatch,
    changed_by: str,
) -> dict[str, Any]:
    data = _model_data(payload, exclude_unset=True)
    after = _require(
        repository.patch_country_profile(connection, country_slug, data),
        "Country profile",
    )
    if after.get("status") == PublicationStatus.published.value:
        _validate_country_profile_for_publish(after)
    _audit(
        connection, "country_profile", after, "updated", changed_by, {"after": after}
    )
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
        _validate_user_story_for_publish(data)
    row = repository.create_user_story_for_admin(connection, data)
    _audit(connection, "user_story", row, "created", changed_by, {"after": row})
    return row


def patch_user_story(
    connection: Connection[Any],
    story_id: str,
    payload: UserStoryPatch,
    changed_by: str,
) -> dict[str, Any]:
    before = _require(
        repository.get_user_story_for_admin(connection, story_id), "User story"
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
    after = _require(
        repository.patch_user_story_for_admin(connection, story_id, data),
        "User story",
    )
    if after.get("status") == PublicationStatus.published.value:
        _validate_user_story_for_publish(after)
    _audit(
        connection,
        "user_story",
        after,
        _audit_action(before, after),
        changed_by,
        _diff(before, after),
    )
    return after


def _model_data(model: Any, exclude_unset: bool = False) -> dict[str, Any]:
    data = model.model_dump(exclude_unset=exclude_unset, mode="json")
    return {
        key: (value.value if isinstance(value, PublicationStatus) else value)
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


def _validate_source_exists(connection: Connection[Any], source_id: Any) -> None:
    if source_id is None:
        return
    if repository.get_source_for_admin(connection, str(source_id)) is None:
        raise api_error(
            404, "source_not_found", "Source not found.", {"source_id": str(source_id)}
        )


def _validate_legal_signal_exists(
    connection: Connection[Any], legal_signal_id: Any
) -> None:
    if legal_signal_id is None:
        return
    if repository.get_legal_signal_for_admin(connection, str(legal_signal_id)) is None:
        raise api_error(
            404,
            "legal_signal_not_found",
            "Legal signal not found.",
            {"legal_signal_id": str(legal_signal_id)},
        )


def _validate_source_for_publish(data: dict[str, Any]) -> None:
    _require_fields(
        data,
        ["title", "url", "publisher", "source_type", "confidence"],
        "Source cannot be published because required fields are missing.",
    )


def _validate_legal_signal_for_publish(data: dict[str, Any]) -> None:
    _require_fields(
        data,
        [
            "country_id",
            "source_id",
            "signal_type",
            "impact_direction",
            "impact_level",
            "confidence",
        ],
        "Legal signal cannot be published because required fields are missing.",
    )
    if not (data.get("title_en") or data.get("title")):
        _content_validation_error(
            "Legal signal cannot be published because required fields are missing.",
            ["title_en"],
        )
    if not (data.get("summary_en") or data.get("summary")):
        _content_validation_error(
            "Legal signal cannot be published because required fields are missing.",
            ["summary_en"],
        )


def _validate_evidence_for_publish(data: dict[str, Any]) -> None:
    _require_fields(
        data,
        ["source_id", "country_id", "claim", "confidence"],
        "Evidence item cannot be published because required fields are missing.",
    )


def _validate_country_profile_for_publish(data: dict[str, Any]) -> None:
    fields = [
        "executive_summary",
        "migration_overview",
        "tax_overview",
        "cost_of_living_overview",
        "business_overview",
        "safety_overview",
        "legal_signals_summary",
        "risk_summary",
        "source_summary",
    ]
    if not any(data.get(field) for field in fields):
        _content_validation_error(
            "Country profile cannot be published because public text is empty.",
            fields,
        )


def _validate_user_story_for_publish(data: dict[str, Any]) -> None:
    if data.get("is_synthetic"):
        notes = str(data.get("notes") or "").lower()
        if data.get("verification_status") != "synthetic" or not (
            "synthetic" in notes or "demo" in notes
        ):
            _content_validation_error(
                "Synthetic user story cannot be published without explicit marking.",
                ["verification_status", "notes"],
            )


def _require_fields(data: dict[str, Any], fields: list[str], message: str) -> None:
    missing = [field for field in fields if data.get(field) in (None, "")]
    if missing:
        _content_validation_error(message, missing)


def _content_validation_error(message: str, missing_fields: list[str]) -> None:
    raise api_error(
        422,
        "content_validation_failed",
        message,
        {"missing_fields": missing_fields},
    )


def _require(row: dict[str, Any] | None, entity_name: str) -> dict[str, Any]:
    if row is None:
        raise api_error(404, "not_found", f"{entity_name} not found.")
    return row


def _audit_action(before: dict[str, Any], after: dict[str, Any]) -> str:
    if before.get("status") == after.get("status"):
        return "updated"
    if after.get("status") == PublicationStatus.published.value:
        return "published"
    if after.get("status") == PublicationStatus.archived.value:
        return "archived"
    if after.get("status") == PublicationStatus.rejected.value:
        return "rejected"
    if after.get("status") == PublicationStatus.review.value:
        return "submitted_for_review"
    return "updated"


def _diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    return {"before": before, "after": after}


def _audit(
    connection: Connection[Any],
    entity_type: str,
    entity: dict[str, Any],
    action: str,
    changed_by: str,
    changes: dict[str, Any],
) -> None:
    create_audit_event(
        connection,
        entity_type,
        str(entity["id"]),
        action,
        changed_by,
        changes,
    )
