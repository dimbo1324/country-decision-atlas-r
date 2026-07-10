from app.repositories import retention as repository
from app.services.methodology_config import get_active_methodology_config
from datetime import UTC, datetime, timedelta
from psycopg import Connection
from typing import Any


def run_retention_cleanup(
    connection: Connection[Any], *, dry_run: bool
) -> dict[str, Any]:
    """Delete (or, in dry-run, count) rows past their configured retention
    window across every table the audit flagged as unbounded growth (P1-4,
    Аудит-эпизод 5). Retention windows come from methodology_config.py, not
    hardcoded constants, so they can be tuned per methodology version like
    every other numeric parameter."""
    config = get_active_methodology_config(connection)
    now = datetime.now(UTC)
    analytics_cutoff = now - timedelta(days=config.retention.analytics_days)
    domain_events_cutoff = now - timedelta(
        days=config.retention.domain_events_days
    )
    sessions_cutoff = now - timedelta(days=config.retention.sessions_days)

    if dry_run:
        analytics_events_deleted = repository.count_expired_analytics_events(
            connection, analytics_cutoff
        )
        ai_interaction_logs_deleted = (
            repository.count_expired_ai_interaction_logs(
                connection, analytics_cutoff
            )
        )
        domain_events_deleted = repository.count_relayed_domain_events(
            connection, domain_events_cutoff
        )
        auth_sessions_deleted = repository.count_expired_auth_sessions(
            connection, sessions_cutoff
        )
    else:
        analytics_events_deleted = repository.delete_expired_analytics_events(
            connection, analytics_cutoff
        )
        ai_interaction_logs_deleted = (
            repository.delete_expired_ai_interaction_logs(
                connection, analytics_cutoff
            )
        )
        domain_events_deleted = repository.delete_relayed_domain_events(
            connection, domain_events_cutoff
        )
        auth_sessions_deleted = repository.delete_expired_auth_sessions(
            connection, sessions_cutoff
        )

    return {
        "ok": True,
        "dry_run": dry_run,
        "methodology_version": config.version,
        "cutoffs": {
            "analytics_days": config.retention.analytics_days,
            "domain_events_days": config.retention.domain_events_days,
            "sessions_days": config.retention.sessions_days,
        },
        "summary": {
            "analytics_events_deleted": analytics_events_deleted,
            "ai_interaction_logs_deleted": ai_interaction_logs_deleted,
            "domain_events_deleted": domain_events_deleted,
            "auth_sessions_deleted": auth_sessions_deleted,
        },
    }
