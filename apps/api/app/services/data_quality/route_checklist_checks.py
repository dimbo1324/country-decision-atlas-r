from app.repositories import (
    data_quality as repository,
    route_checklists as route_checklists_repository,
)
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality._issues import _check, _issue
from psycopg import Connection
from typing import Any


def _append_route_checklist_checks(
    connection: Connection[Any],
    issues: list[DataQualityIssue],
    checks: list[DataQualityCheck],
) -> None:
    for row in repository.list_published_checklist_items_missing_title(connection):
        issues.append(
            _issue(
                "route_checklist_item_missing_title",
                "critical",
                "route_checklist_item",
                row.get("id"),
                "Published route checklist item is missing a title.",
                row,
            )
        )
    checks.append(
        _check(
            "route_checklist_items_have_title",
            issues,
            ["route_checklist_item_missing_title"],
        )
    )

    for row in repository.list_duplicate_step_order_checklist_items(connection):
        issues.append(
            _issue(
                "route_checklist_item_duplicate_step_order",
                "critical",
                "route_checklist_item",
                row.get("route_id"),
                "Route checklist items have duplicate step_order for the same route.",
                row,
            )
        )
    checks.append(
        _check(
            "route_checklist_step_orders_unique",
            issues,
            ["route_checklist_item_duplicate_step_order"],
        )
    )

    for row in (
        route_checklists_repository.list_published_checklist_items_without_traceability(
            connection
        )
    ):
        issues.append(
            _issue(
                "route_checklist_item_missing_traceability",
                "critical",
                "route_checklist_item",
                row.get("id"),
                "Published route checklist item has no source or evidence reference.",
                row,
            )
        )
    checks.append(
        _check(
            "route_checklist_items_have_traceability",
            issues,
            ["route_checklist_item_missing_traceability"],
        )
    )

    for row in route_checklists_repository.list_orphan_checklist_items(connection):
        issues.append(
            _issue(
                "route_checklist_item_for_unpublished_route",
                "critical",
                "route_checklist_item",
                row.get("id"),
                "Published route checklist item belongs to a non-published route.",
                row,
            )
        )
    checks.append(
        _check(
            "route_checklist_items_route_published",
            issues,
            ["route_checklist_item_for_unpublished_route"],
        )
    )
