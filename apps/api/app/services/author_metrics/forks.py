from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import author_metrics as repository
from app.services.author_metrics import definitions, helpers
from psycopg import Connection
from typing import Any


def fork_definition(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    source_definition_id: str,
    slug: str,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    definitions._validate_slug(slug)
    source = repository.get_definition_by_id(connection, source_definition_id)
    if (
        source is None
        or source["status"] != "published"
        or source["visibility"] != "public"
    ):
        raise api_error(
            404,
            "author_metric_not_found",
            "Author metric definition was not found.",
            {},
        )
    if repository.get_definition_by_author_slug(
        connection, current_user.id, slug
    ):
        raise api_error(
            409,
            "author_metric_slug_taken",
            "You already have an author metric with this slug.",
            {},
        )
    forked = repository.create_definition(
        connection,
        author_user_id=current_user.id,
        slug=slug,
        name_en=source["name_en"],
        name_ru=source["name_ru"],
        methodology_en=source["methodology_en"],
        methodology_ru=source["methodology_ru"],
        polarity=source["polarity"],
        scale_min=source["scale_min"],
        scale_max=source["scale_max"],
        license=source["license"],
        visibility="private",
        forked_from_id=source["id"],
    )
    helpers._audit(
        connection,
        forked,
        "created",
        current_user,
        {"forked_from_id": {"new": source["id"]}},
    )
    helpers._track_event(
        connection,
        "author_metric_forked",
        entity_id=forked["id"],
        metadata={"forked_from_id": source["id"]},
    )
    return helpers._my_definition(forked)
