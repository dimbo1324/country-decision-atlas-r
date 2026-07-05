from app.repositories.audit import list_audit_events
from psycopg import Connection
from typing import Any


_REJECT_LIKE_ACTIONS = frozenset({"rejected", "hidden", "report_resolved"})
_ANOMALY_MIN_ACTIONS = 5
_ANOMALY_REJECT_RATE_THRESHOLD = 0.5


def list_moderation_actions(
    connection: Connection[Any],
    *,
    entity_type: str | None,
    action: str | None,
    changed_by: str | None,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    rows = list_audit_events(
        connection,
        entity_type=entity_type,
        action=action,
        changed_by=changed_by,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [_entry(row) for row in rows],
        "total": _total(rows),
        "anomalies": _detect_anomalies(rows),
    }


def _entry(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "entity_type": row["entity_type"],
        "entity_id": str(row["entity_id"]),
        "action": row["action"],
        "changed_by": row["changed_by"],
        "changed_at": row["changed_at"],
        "changes": row.get("changes") or {},
    }


def _total(rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    return int(rows[0].get("total_count") or len(rows))


def _detect_anomalies(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, dict[str, int]] = {}
    for row in rows:
        moderator = str(row["changed_by"])
        bucket = counts.setdefault(moderator, {"total": 0, "reject_like": 0})
        bucket["total"] += 1
        if row["action"] in _REJECT_LIKE_ACTIONS:
            bucket["reject_like"] += 1
    anomalies = []
    for moderator, bucket in counts.items():
        if bucket["total"] < _ANOMALY_MIN_ACTIONS:
            continue
        reject_rate = bucket["reject_like"] / bucket["total"]
        if reject_rate >= _ANOMALY_REJECT_RATE_THRESHOLD:
            anomalies.append(
                {
                    "changed_by": moderator,
                    "total_actions": bucket["total"],
                    "reject_like_actions": bucket["reject_like"],
                    "reject_rate": round(reject_rate, 2),
                }
            )
    return sorted(anomalies, key=lambda item: item["reject_rate"], reverse=True)
