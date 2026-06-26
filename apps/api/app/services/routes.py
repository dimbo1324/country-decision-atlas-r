from app.core.errors import api_error
from app.repositories import (
    countries as countries_repository,
    routes as routes_repository,
)
from app.repositories.audit import insert_audit_event
from app.repositories.domain_events import insert_domain_event
from app.schemas.common import (
    LocaleResolution,
    Pagination,
    TranslationStatus,
    locale_resolution,
)
from app.schemas.routes import (
    EligibilityFlag,
    RouteDetailResponse,
    RouteEligibility,
    RouteListItem,
    RouteListResponse,
    RouteType,
)
from app.services.publication import (
    audit_action_for_transition,
    ensure_allowed_transition,
    is_publish_transition,
)
from psycopg import Connection
from typing import Any
from uuid import UUID


def list_country_routes(
    connection: Connection[Any],
    country_slug: str,
    locale: str,
    route_type: RouteType | str | None = None,
    allows_work: EligibilityFlag | str | None = None,
    allows_family: EligibilityFlag | str | None = None,
    leads_to_pr: EligibilityFlag | str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> RouteListResponse:
    if countries_repository.get_country(connection, country_slug, locale) is None:
        raise api_error(
            404,
            "country_not_found",
            "Country not found.",
            {"country_slug": country_slug},
        )
    rows = routes_repository.list_routes_by_country(
        connection,
        country_slug,
        locale,
        _enum_value(route_type),
        _enum_value(allows_work),
        _enum_value(allows_family),
        _enum_value(leads_to_pr),
        limit,
        offset,
    )
    total = int(rows[0]["total_count"]) if rows else 0
    items = [RouteListItem(**_with_eligibility(_strip_internal(row))) for row in rows]
    return RouteListResponse(
        items=items,
        pagination=Pagination(limit=limit, offset=offset, total=total),
        locale=_route_locale(locale),
    )


def get_route_detail(
    connection: Connection[Any],
    route_id: str,
    locale: str,
) -> RouteDetailResponse:
    row = routes_repository.get_route_by_id(connection, route_id, locale)
    if row is None:
        raise api_error(
            404,
            "route_not_found",
            "Route not found.",
            {"route_id": route_id},
        )
    return _route_detail_response(connection, row, locale)


def get_route_detail_by_slug(
    connection: Connection[Any],
    country_slug: str,
    route_slug: str,
    locale: str,
) -> RouteDetailResponse:
    row = routes_repository.get_route_by_slug(
        connection, country_slug, route_slug, locale
    )
    if row is None:
        raise api_error(
            404,
            "route_not_found",
            "Route not found.",
            {"country_slug": country_slug, "route_slug": route_slug},
        )
    return _route_detail_response(connection, row, locale)


def change_route_status(
    connection: Connection[Any],
    route_id: str,
    new_status: str,
    changed_by: str,
) -> dict[str, Any]:
    with connection.transaction():
        before = routes_repository.get_route_for_admin(connection, route_id)
        if before is None:
            raise api_error(
                404,
                "route_not_found",
                "Route not found.",
                {"route_id": route_id},
            )
        old_status = str(before.get("status") or "")
        ensure_allowed_transition(old_status, new_status)
        after = routes_repository.patch_route_status(connection, route_id, new_status)
        _audit_status_change(connection, before, after, changed_by)
        _emit_route_published_event(connection, before, after)
    return after


def publish_route(
    connection: Connection[Any],
    route_id: str,
    changed_by: str,
) -> dict[str, Any]:
    return change_route_status(connection, route_id, "published", changed_by)


def _route_detail_response(
    connection: Connection[Any],
    row: dict[str, Any],
    locale: str,
) -> RouteDetailResponse:
    route_id = str(row["id"])
    documents = routes_repository.list_route_documents(connection, route_id, locale)
    sources = routes_repository.list_route_sources(connection, route_id)
    evidence = routes_repository.list_route_evidence(connection, route_id)
    return RouteDetailResponse(
        **_with_eligibility(row),
        documents=documents,
        sources=sources,
        evidence=evidence,
        locale=_route_locale(locale),
    )


def _strip_internal(row: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in row.items() if k != "total_count"}


def _with_eligibility(row: dict[str, Any]) -> dict[str, Any]:
    return {
        **row,
        "eligibility": RouteEligibility(
            allows_work=row["allows_work"],
            allows_family=row["allows_family"],
            leads_to_pr=row["leads_to_pr"],
            leads_to_citizenship=row["leads_to_citizenship"],
            requires_income_proof=row["requires_income_proof"],
            requires_local_address=row["requires_local_address"],
            requires_criminal_record_check=row["requires_criminal_record_check"],
        ),
    }


def _audit_status_change(
    connection: Connection[Any],
    before: dict[str, Any],
    after: dict[str, Any],
    changed_by: str,
) -> None:
    old_status = str(before.get("status") or "")
    new_status = str(after.get("status") or "")
    insert_audit_event(
        connection,
        entity_type="route",
        entity_id=_as_uuid(after["id"]),
        action=audit_action_for_transition(old_status, new_status),
        changed_by=changed_by,
        changes={"status": {"old": old_status, "new": new_status}},
    )


def _emit_route_published_event(
    connection: Connection[Any],
    before: dict[str, Any],
    after: dict[str, Any],
) -> None:
    if not is_publish_transition(str(before.get("status")), str(after.get("status"))):
        return
    route_id = str(after["id"])
    country_slug = after.get("country_slug")
    insert_domain_event(
        connection,
        event_key=f"route:{route_id}:route.published",
        event_type="route.published",
        aggregate_type="route",
        aggregate_id=_as_uuid(route_id),
        country_slug=country_slug,
        payload={
            "id": route_id,
            "slug": after.get("slug"),
            "country_slug": country_slug,
            "route_type": after.get("route_type"),
            "title": after.get("title") or after.get("title_ru"),
            "legal_status": after.get("legal_status"),
            "allows_work": after.get("allows_work"),
            "allows_family": after.get("allows_family"),
            "leads_to_pr": after.get("leads_to_pr"),
            "leads_to_citizenship": after.get("leads_to_citizenship"),
        },
        status="pending",
        notifiable=True,
    )


def _enum_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value.value)


def _route_locale(locale: str) -> LocaleResolution:
    if locale == "en":
        return locale_resolution(locale, "en", TranslationStatus.source)
    return locale_resolution(locale, locale, TranslationStatus.fallback)


def _as_uuid(value: Any) -> UUID:
    return value if isinstance(value, UUID) else UUID(str(value))
