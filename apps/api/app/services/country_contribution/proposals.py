from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import country_contribution as repository
from app.services.country_contribution import helpers
from app.services.list_helpers import total_from_window_count
from app.services.publication import ensure_allowed_transition
from psycopg import Connection, errors as psycopg_errors
from typing import Any


def _constraint_name(exc: psycopg_errors.UniqueViolation) -> str:
    return (exc.diag.constraint_name or "").lower()


def create_proposal(
    connection: Connection[Any], *, current_user: CurrentUser, payload: Any
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    helpers.validate_slug(payload.slug)
    iso2 = payload.iso2.upper()
    iso3 = payload.iso3.upper()
    helpers.validate_iso_codes(iso2, iso3)
    if repository.country_slug_exists(connection, payload.slug):
        raise api_error(
            409,
            "country_slug_taken",
            "A country with this slug already exists.",
            {},
        )
    if repository.country_iso_exists(connection, iso2, iso3):
        raise api_error(
            409,
            "country_iso_taken",
            "A country with this ISO code already exists.",
            {},
        )
    try:
        with connection.transaction():
            country = repository.create_country_shell(
                connection,
                slug=payload.slug,
                iso2=iso2,
                iso3=iso3,
                name_en=payload.name_en,
            )
            repository.create_country_name_translation(
                connection,
                country_id=str(country["id"]),
                name_ru=payload.name_ru,
            )
            created = repository.create_proposal_row(
                connection,
                proposer_user_id=current_user.id,
                country_id=str(country["id"]),
                slug=payload.slug,
                name_en=payload.name_en,
                name_ru=payload.name_ru,
                iso2=iso2,
                iso3=iso3,
                justification=payload.justification,
            )
            helpers._audit(
                connection,
                str(created["id"]),
                "created",
                current_user.id,
                {"status": {"new": "draft"}, "slug": {"new": payload.slug}},
            )
    except psycopg_errors.UniqueViolation as exc:
        constraint = _constraint_name(exc)
        if "iso" in constraint:
            raise api_error(
                409,
                "country_iso_taken",
                "A country with this ISO code already exists.",
                {},
            ) from exc
        raise api_error(
            409,
            "country_slug_taken",
            "A country with this slug already exists.",
            {},
        ) from exc
    proposal = helpers.get_proposal_or_404(connection, str(created["id"]))
    return helpers._proposal_view(proposal)


def patch_my_proposal(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    proposal_id: str,
    payload: Any,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    helpers.get_owner_proposal_or_404(connection, proposal_id, current_user.id)
    updated = repository.update_justification(
        connection,
        proposal_id=proposal_id,
        proposer_user_id=current_user.id,
        justification=payload.justification,
    )
    if updated is None:
        raise api_error(
            409,
            "country_proposal_not_editable",
            "Country proposal can only be edited while it is a draft.",
            {},
        )
    helpers._audit(
        connection,
        proposal_id,
        "updated",
        current_user.id,
        {"justification": {"new": payload.justification}},
    )
    return helpers._proposal_view(
        helpers.get_proposal_or_404(connection, proposal_id)
    )


def list_my_proposals(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    rows = repository.list_proposals_for_user(
        connection, current_user.id, limit=limit, offset=offset
    )
    return {
        "items": [helpers._proposal_view(row) for row in rows],
        "total": total_from_window_count(rows),
    }


def get_my_proposal(
    connection: Connection[Any], *, current_user: CurrentUser, proposal_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    return helpers._proposal_view(
        helpers.get_owner_proposal_or_404(
            connection, proposal_id, current_user.id
        )
    )


def submit_my_proposal(
    connection: Connection[Any], *, current_user: CurrentUser, proposal_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    proposal = helpers.get_owner_proposal_or_404(
        connection, proposal_id, current_user.id
    )
    ensure_allowed_transition(proposal["status"], "review")
    updated = repository.apply_status_transition(
        connection,
        proposal_id,
        old_status=proposal["status"],
        new_status="review",
    )
    if updated is None:
        raise api_error(
            409,
            "invalid_status_transition",
            "Country proposal cannot be submitted for review.",
            {},
        )
    helpers._audit(
        connection,
        proposal_id,
        "submitted_for_review",
        current_user.id,
        {"status": {"old": proposal["status"], "new": "review"}},
    )
    return helpers._proposal_view(
        helpers.get_proposal_or_404(connection, proposal_id)
    )
