"""Data-quality checks for route checklists: missing traceability, duplicate step order, missing titles."""

from app.repositories import (
    data_quality as dq_repository,
    route_checklists as route_checklists_repository,
)
from app.schemas.data_quality import DataQualityCheck, DataQualityIssue
from app.services.data_quality.route_checklist_checks import (
    _append_route_checklist_checks,
)
from psycopg import Connection
from typing import Any, cast


CONNECTION = cast(Connection[Any], object())


def test_detects_missing_traceability(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        dq_repository, "list_published_checklist_items_missing_title", lambda *_: []
    )
    monkeypatch.setattr(
        dq_repository, "list_duplicate_step_order_checklist_items", lambda *_: []
    )
    monkeypatch.setattr(
        route_checklists_repository,
        "list_published_checklist_items_without_traceability",
        lambda *_: [
            {
                "id": "item-1",
                "route_slug": "temporary-legal-residence",
                "country_slug": "uruguay",
            }
        ],
    )
    monkeypatch.setattr(
        route_checklists_repository, "list_orphan_checklist_items", lambda *_: []
    )

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_route_checklist_checks(CONNECTION, issues, checks)

    codes = [issue.code for issue in issues]
    assert "route_checklist_item_missing_traceability" in codes
    traceability_check = next(
        c for c in checks if c.code == "route_checklist_items_have_traceability"
    )
    assert traceability_check.status == "failed"


def test_passes_when_traceability_present(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        dq_repository, "list_published_checklist_items_missing_title", lambda *_: []
    )
    monkeypatch.setattr(
        dq_repository, "list_duplicate_step_order_checklist_items", lambda *_: []
    )
    monkeypatch.setattr(
        route_checklists_repository,
        "list_published_checklist_items_without_traceability",
        lambda *_: [],
    )
    monkeypatch.setattr(
        route_checklists_repository, "list_orphan_checklist_items", lambda *_: []
    )

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_route_checklist_checks(CONNECTION, issues, checks)

    traceability_check = next(
        c for c in checks if c.code == "route_checklist_items_have_traceability"
    )
    assert traceability_check.status == "passed"


def test_detects_duplicate_step_order(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        dq_repository, "list_published_checklist_items_missing_title", lambda *_: []
    )
    monkeypatch.setattr(
        dq_repository,
        "list_duplicate_step_order_checklist_items",
        lambda *_: [
            {
                "route_id": "route-1",
                "route_slug": "temporary-legal-residence",
                "country_slug": "uruguay",
                "step_order": 1,
                "item_count": 2,
            }
        ],
    )
    monkeypatch.setattr(
        route_checklists_repository,
        "list_published_checklist_items_without_traceability",
        lambda *_: [],
    )
    monkeypatch.setattr(
        route_checklists_repository, "list_orphan_checklist_items", lambda *_: []
    )

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_route_checklist_checks(CONNECTION, issues, checks)

    codes = [issue.code for issue in issues]
    assert "route_checklist_item_duplicate_step_order" in codes
    step_order_check = next(
        c for c in checks if c.code == "route_checklist_step_orders_unique"
    )
    assert step_order_check.status == "failed"


def test_detects_missing_title(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        dq_repository,
        "list_published_checklist_items_missing_title",
        lambda *_: [
            {
                "id": "item-1",
                "route_slug": "temporary-legal-residence",
                "country_slug": "uruguay",
            }
        ],
    )
    monkeypatch.setattr(
        dq_repository, "list_duplicate_step_order_checklist_items", lambda *_: []
    )
    monkeypatch.setattr(
        route_checklists_repository,
        "list_published_checklist_items_without_traceability",
        lambda *_: [],
    )
    monkeypatch.setattr(
        route_checklists_repository, "list_orphan_checklist_items", lambda *_: []
    )

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_route_checklist_checks(CONNECTION, issues, checks)

    codes = [issue.code for issue in issues]
    assert "route_checklist_item_missing_title" in codes


def test_detects_checklist_item_for_unpublished_route(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        dq_repository, "list_published_checklist_items_missing_title", lambda *_: []
    )
    monkeypatch.setattr(
        dq_repository, "list_duplicate_step_order_checklist_items", lambda *_: []
    )
    monkeypatch.setattr(
        route_checklists_repository,
        "list_published_checklist_items_without_traceability",
        lambda *_: [],
    )
    monkeypatch.setattr(
        route_checklists_repository,
        "list_orphan_checklist_items",
        lambda *_: [
            {
                "id": "item-1",
                "route_slug": "temporary-legal-residence",
                "route_status": "draft",
            }
        ],
    )

    issues: list[DataQualityIssue] = []
    checks: list[DataQualityCheck] = []
    _append_route_checklist_checks(CONNECTION, issues, checks)

    codes = [issue.code for issue in issues]
    assert "route_checklist_item_for_unpublished_route" in codes
