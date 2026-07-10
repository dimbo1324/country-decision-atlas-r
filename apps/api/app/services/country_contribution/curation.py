import json
from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import country_contribution as repository
from app.services.country_contribution import helpers
from app.services.country_onboarding import evaluate_country_onboarding
from app.services.list_helpers import total_from_window_count
from app.services.publication import ensure_allowed_transition
from psycopg import Connection
from typing import Any


def list_proposals_for_curation(
    connection: Connection[Any],
    *,
    status: str | None,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    rows = repository.list_proposals_for_curation(
        connection, status=status, limit=limit, offset=offset
    )
    return {
        "items": [helpers._proposal_view(row) for row in rows],
        "total": total_from_window_count(rows),
    }


def get_proposal_for_curation(
    connection: Connection[Any], proposal_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    return helpers._proposal_view(
        helpers.get_proposal_or_404(connection, proposal_id)
    )


def assign_curator(
    connection: Connection[Any], *, current_user: CurrentUser, proposal_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = helpers.get_proposal_or_404(connection, proposal_id)
    updated = repository.assign_curator(
        connection, proposal_id=proposal_id, curator_user_id=current_user.id
    )
    if updated is None:
        raise api_error(
            409,
            "curator_already_assigned",
            "This country proposal already has a curator.",
            {"curator_user_id": proposal.get("curator_user_id")},
        )
    helpers._audit(
        connection,
        proposal_id,
        "updated",
        current_user.id,
        {"curator_user_id": {"new": current_user.id}},
    )
    return helpers._proposal_view(
        helpers.get_proposal_or_404(connection, proposal_id)
    )


def run_readiness_check(
    connection: Connection[Any], *, current_user: CurrentUser, proposal_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = helpers.get_proposal_or_404(connection, proposal_id)
    was_active = bool(proposal["country_is_active"])
    with connection.transaction():
        if not was_active:
            repository.set_country_active(
                connection, country_id=proposal["country_id"], is_active=True
            )
        result = evaluate_country_onboarding(connection, proposal["slug"])
        if not was_active:
            repository.set_country_active(
                connection, country_id=proposal["country_id"], is_active=False
            )
        snapshot = result.model_dump(mode="json")
        repository.store_readiness_snapshot(
            connection,
            proposal_id=proposal_id,
            snapshot_json=json.dumps(snapshot, default=str),
        )
        helpers._audit(
            connection,
            proposal_id,
            "updated",
            current_user.id,
            {"readiness_check": {"new": result.mvp_ready}},
        )
    return snapshot


def publish_proposal(
    connection: Connection[Any], *, current_user: CurrentUser, proposal_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = helpers.get_proposal_or_404(connection, proposal_id)
    if proposal.get("curator_user_id") is None:
        raise api_error(
            409,
            "curator_required",
            "A curator must be assigned before this country proposal can be published.",
            {},
        )
    ensure_allowed_transition(proposal["status"], "published")
    with connection.transaction():
        repository.set_country_active(
            connection, country_id=proposal["country_id"], is_active=True
        )
        result = evaluate_country_onboarding(connection, proposal["slug"])
        if not result.mvp_ready:
            raise api_error(
                422,
                "onboarding_gate_failed",
                "This country has not passed the onboarding readiness gate yet.",
                {
                    "findings": [
                        f.model_dump(mode="json") for f in result.findings
                    ]
                },
            )
        repository.store_readiness_snapshot(
            connection,
            proposal_id=proposal_id,
            snapshot_json=json.dumps(
                result.model_dump(mode="json"), default=str
            ),
        )
        updated = repository.apply_status_transition(
            connection,
            proposal_id,
            old_status=proposal["status"],
            new_status="published",
            moderated_by=current_user.id,
            set_published_at=True,
        )
        if updated is None:
            raise api_error(
                409,
                "invalid_status_transition",
                "Country proposal cannot be published.",
                {},
            )
        helpers._audit(
            connection,
            proposal_id,
            "published",
            current_user.id,
            {"status": {"old": proposal["status"], "new": "published"}},
        )
    return helpers._proposal_view(
        helpers.get_proposal_or_404(connection, proposal_id)
    )


def reject_proposal(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    reason: str,
) -> dict[str, Any]:
    return _moderate_transition(
        connection,
        current_user=current_user,
        proposal_id=proposal_id,
        new_status="rejected",
        reason=reason,
        audit_action="rejected",
    )


def request_changes(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    reason: str,
) -> dict[str, Any]:
    return _moderate_transition(
        connection,
        current_user=current_user,
        proposal_id=proposal_id,
        new_status="draft",
        reason=reason,
        audit_action="updated",
    )


def archive_proposal(
    connection: Connection[Any], *, current_user: CurrentUser, proposal_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = helpers.get_proposal_or_404(connection, proposal_id)
    ensure_allowed_transition(proposal["status"], "archived")
    updated = repository.apply_status_transition(
        connection,
        proposal_id,
        old_status=proposal["status"],
        new_status="archived",
        moderated_by=current_user.id,
    )
    if updated is None:
        raise api_error(
            409,
            "invalid_status_transition",
            "Country proposal cannot be archived.",
            {},
        )
    repository.set_country_active(
        connection, country_id=proposal["country_id"], is_active=False
    )
    helpers._audit(
        connection,
        proposal_id,
        "archived",
        current_user.id,
        {"status": {"old": proposal["status"], "new": "archived"}},
    )
    return helpers._proposal_view(
        helpers.get_proposal_or_404(connection, proposal_id)
    )


def _moderate_transition(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    new_status: str,
    reason: str,
    audit_action: str,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = helpers.get_proposal_or_404(connection, proposal_id)
    ensure_allowed_transition(proposal["status"], new_status)
    updated = repository.apply_status_transition(
        connection,
        proposal_id,
        old_status=proposal["status"],
        new_status=new_status,
        moderated_by=current_user.id,
        moderation_reason=reason,
    )
    if updated is None:
        raise api_error(
            409,
            "invalid_status_transition",
            "Country proposal status could not be changed.",
            {},
        )
    helpers._audit(
        connection,
        proposal_id,
        audit_action,
        current_user.id,
        {
            "status": {"old": proposal["status"], "new": new_status},
            "reason": reason,
        },
    )
    return helpers._proposal_view(
        helpers.get_proposal_or_404(connection, proposal_id)
    )
