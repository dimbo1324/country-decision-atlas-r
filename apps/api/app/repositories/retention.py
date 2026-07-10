from app.core.database import fetch_one
from datetime import datetime
from psycopg import Connection
from typing import Any


def count_expired_analytics_events(
    connection: Connection[Any], cutoff: datetime
) -> int:
    row = fetch_one(
        connection,
        "SELECT COUNT(*) AS cnt FROM analytics_events WHERE created_at < %s",
        (cutoff,),
    )
    return int(row["cnt"]) if row else 0


def delete_expired_analytics_events(
    connection: Connection[Any], cutoff: datetime
) -> int:
    row = fetch_one(
        connection,
        """
        WITH deleted AS (
            DELETE FROM analytics_events
            WHERE created_at < %s
            RETURNING id
        )
        SELECT COUNT(*) AS cnt FROM deleted
        """,
        (cutoff,),
    )
    return int(row["cnt"]) if row else 0


def count_expired_ai_interaction_logs(
    connection: Connection[Any], cutoff: datetime
) -> int:
    row = fetch_one(
        connection,
        "SELECT COUNT(*) AS cnt FROM ai_interaction_logs WHERE created_at < %s",
        (cutoff,),
    )
    return int(row["cnt"]) if row else 0


def delete_expired_ai_interaction_logs(
    connection: Connection[Any], cutoff: datetime
) -> int:
    row = fetch_one(
        connection,
        """
        WITH deleted AS (
            DELETE FROM ai_interaction_logs
            WHERE created_at < %s
            RETURNING id
        )
        SELECT COUNT(*) AS cnt FROM deleted
        """,
        (cutoff,),
    )
    return int(row["cnt"]) if row else 0


def count_relayed_domain_events(
    connection: Connection[Any], cutoff: datetime
) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS cnt FROM domain_events
        WHERE status = 'relayed' AND relayed_at < %s
        """,
        (cutoff,),
    )
    return int(row["cnt"]) if row else 0


def delete_relayed_domain_events(
    connection: Connection[Any], cutoff: datetime
) -> int:
    """Only status='relayed' rows are eligible. pending/in_flight/failed
    events must never be swept by retention — they still need delivery or
    investigation; deleting them would silently drop outbox work."""
    row = fetch_one(
        connection,
        """
        WITH deleted AS (
            DELETE FROM domain_events
            WHERE status = 'relayed' AND relayed_at < %s
            RETURNING id
        )
        SELECT COUNT(*) AS cnt FROM deleted
        """,
        (cutoff,),
    )
    return int(row["cnt"]) if row else 0


def count_expired_auth_sessions(
    connection: Connection[Any], cutoff: datetime
) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS cnt FROM auth_sessions
        WHERE (revoked_at IS NOT NULL AND revoked_at < %s)
           OR expires_at < %s
        """,
        (cutoff, cutoff),
    )
    return int(row["cnt"]) if row else 0


def delete_expired_auth_sessions(
    connection: Connection[Any], cutoff: datetime
) -> int:
    """Sessions past their retention window: either revoked more than
    `cutoff` ago, or naturally expired more than `cutoff` ago (regardless of
    revocation, so an old never-revoked session is still swept once its own
    expiry is far enough in the past)."""
    row = fetch_one(
        connection,
        """
        WITH deleted AS (
            DELETE FROM auth_sessions
            WHERE (revoked_at IS NOT NULL AND revoked_at < %s)
               OR expires_at < %s
            RETURNING id
        )
        SELECT COUNT(*) AS cnt FROM deleted
        """,
        (cutoff, cutoff),
    )
    return int(row["cnt"]) if row else 0
