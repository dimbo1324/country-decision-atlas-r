from app.repositories import author_metrics as repository
from app.services import feature_flags as feature_flags_service
from app.services.author_metrics import helpers
from datetime import UTC, datetime
from psycopg import Connection
from typing import Any


METHODOLOGY_VERSION = "v1.0"
FRESHNESS_FRESH_DAYS = 180
FRESHNESS_AGING_DAYS = 365


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def compute_coverage_score(
    *, published_metric_count: int, total_values: int, active_country_count: int
) -> float:
    if published_metric_count == 0 or active_country_count == 0:
        return 0.0
    ratio = total_values / (published_metric_count * active_country_count)
    return _clamp(ratio * 100.0)


def compute_freshness_score(
    last_value_updated_at: datetime | None, now: datetime
) -> float:
    if last_value_updated_at is None:
        return 0.0
    reference = (
        last_value_updated_at.replace(tzinfo=UTC)
        if last_value_updated_at.tzinfo is None
        else last_value_updated_at
    )
    days = (now - reference).days
    if days <= FRESHNESS_FRESH_DAYS:
        return 100.0
    if days <= FRESHNESS_AGING_DAYS:
        return 60.0
    return 20.0


def compute_sourcing_score(*, sourced_values: int, total_values: int) -> float:
    if total_values == 0:
        return 0.0
    return _clamp((sourced_values / total_values) * 100.0)


def get_reputation_for_author(
    connection: Connection[Any], author_user_id: str
) -> dict[str, Any] | None:
    helpers.ensure_feature_enabled(connection)
    row = repository.get_author_reputation(connection, author_user_id)
    return helpers._reputation(row) if row else None


def compute_and_store_reputation_for_author(
    connection: Connection[Any],
    author_user_id: str,
    now: datetime | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    effective_now = now or _now()
    result: dict[str, Any] = {
        "author_user_id": author_user_id,
        "feature_enabled": True,
        "dry_run": dry_run,
        "computed": False,
        "stored": False,
        "error": None,
    }
    if not feature_flags_service.is_feature_enabled_by_key(
        connection, helpers.FEATURE_KEY
    ):
        result["feature_enabled"] = False
        return result
    try:
        inputs = repository.get_reputation_inputs_for_author(
            connection, author_user_id
        )
        published_metric_count = int(inputs.get("published_metric_count") or 0)
        total_values = int(inputs.get("total_values") or 0)
        sourced_values = int(inputs.get("sourced_values") or 0)
        active_country_count = int(inputs.get("active_country_count") or 0)
        last_value_updated_at = inputs.get("last_value_updated_at")
        subscriber_count = repository.count_subscribers_for_author(
            connection, author_user_id
        )
        payload = {
            "author_user_id": author_user_id,
            "coverage_score": compute_coverage_score(
                published_metric_count=published_metric_count,
                total_values=total_values,
                active_country_count=active_country_count,
            ),
            "freshness_score": compute_freshness_score(
                last_value_updated_at, effective_now
            ),
            "sourcing_score": compute_sourcing_score(
                sourced_values=sourced_values, total_values=total_values
            ),
            "subscriber_count": subscriber_count,
            "published_metric_count": published_metric_count,
            "computed_at": effective_now,
            "methodology_version": METHODOLOGY_VERSION,
        }
        result["computed"] = True
        result.update(
            {
                key: payload[key]
                for key in (
                    "coverage_score",
                    "freshness_score",
                    "sourcing_score",
                    "subscriber_count",
                    "published_metric_count",
                )
            }
        )
        if not dry_run:
            repository.upsert_author_reputation(connection, payload)
            result["stored"] = True
    except Exception as exc:
        result["error"] = str(exc)
    return result


def compute_and_store_reputation_for_all_authors(
    connection: Connection[Any],
    now: datetime | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    effective_now = now or _now()
    summary: dict[str, Any] = {
        "feature_enabled": True,
        "dry_run": dry_run,
        "authors_processed": 0,
        "authors_computed": 0,
        "authors_stored": 0,
        "authors_failed": 0,
        "errors": [],
    }
    if not feature_flags_service.is_feature_enabled_by_key(
        connection, helpers.FEATURE_KEY
    ):
        summary["feature_enabled"] = False
        return summary
    authors = repository.list_authors_with_published_metrics(connection)
    for author in authors:
        author_user_id = author["author_user_id"]
        r = compute_and_store_reputation_for_author(
            connection, author_user_id, now=effective_now, dry_run=dry_run
        )
        summary["authors_processed"] += 1
        if r.get("computed"):
            summary["authors_computed"] += 1
        if r.get("stored"):
            summary["authors_stored"] += 1
        if r.get("error"):
            summary["authors_failed"] += 1
            summary["errors"].append(
                {"author_user_id": author_user_id, "error": r["error"]}
            )
    return summary
