from app.repositories import feature_flags as ff_repo, trust as trust_repo
from app.services.feature_flags import can_access, default_access_context
from app.services.trust_score import compute_trust_score_from_inputs
from datetime import UTC, datetime
from psycopg import Connection
from psycopg.types.json import Jsonb
from typing import Any


FEATURE_KEY = "trust_surface_enabled"


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _is_feature_enabled(connection: Connection[Any]) -> bool:
    feature = ff_repo.get_feature_flag(connection, FEATURE_KEY)
    rules = ff_repo.list_feature_access_rules(connection, FEATURE_KEY)
    from app.core.config import get_settings

    ctx = default_access_context(get_settings())
    decision = can_access(ctx, feature, rules, FEATURE_KEY)
    return decision.is_enabled


def _jsonb_payload(payload: dict[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    if isinstance(out.get("input_summary"), dict):
        out["input_summary"] = Jsonb(out["input_summary"])
    return out


def compute_and_store_trust_for_country(
    connection: Connection[Any],
    country_slug: str,
    now: datetime | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    effective_now = now or _now()
    result: dict[str, Any] = {
        "country_slug": country_slug,
        "feature_enabled": True,
        "country_not_found": False,
        "dry_run": dry_run,
        "computed": False,
        "stored": False,
        "error": None,
    }
    if not _is_feature_enabled(connection):
        result["feature_enabled"] = False
        return result
    inputs = trust_repo.get_trust_inputs_for_country(connection, country_slug)
    if inputs is None:
        result["country_not_found"] = True
        return result
    try:
        payload = compute_trust_score_from_inputs(inputs, effective_now)
        result["computed"] = True
        result["trust_label"] = payload["trust_label"]
        result["trust_score"] = payload["trust_score"]
        result["confidence"] = payload["confidence"]
        result["freshness_status"] = payload["freshness_status"]
        if not dry_run:
            trust_repo.upsert_country_trust_score(connection, _jsonb_payload(payload))
            result["stored"] = True
    except Exception as exc:
        result["error"] = str(exc)
    return result


def compute_and_store_trust_for_all_countries(
    connection: Connection[Any],
    now: datetime | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    effective_now = now or _now()
    summary: dict[str, Any] = {
        "feature_enabled": True,
        "dry_run": dry_run,
        "countries_processed": 0,
        "countries_computed": 0,
        "countries_stored": 0,
        "countries_failed": 0,
        "errors": [],
    }
    if not _is_feature_enabled(connection):
        summary["feature_enabled"] = False
        return summary
    countries = trust_repo.list_active_countries(connection)
    for country in countries:
        slug = country["slug"]
        r = compute_and_store_trust_for_country(
            connection, slug, now=effective_now, dry_run=dry_run
        )
        summary["countries_processed"] += 1
        if r.get("computed"):
            summary["countries_computed"] += 1
        if r.get("stored"):
            summary["countries_stored"] += 1
        if r.get("error"):
            summary["countries_failed"] += 1
            summary["errors"].append({"country_slug": slug, "error": r["error"]})
    return summary
