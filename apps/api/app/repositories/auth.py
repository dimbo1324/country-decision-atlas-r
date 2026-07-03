from app.core.database import execute_one, fetch_all, fetch_one
from datetime import datetime
from psycopg import Connection
from psycopg.types.json import Jsonb
from typing import Any


USER_FIELDS = """
    id::text AS id,
    email,
    display_name,
    role,
    status,
    email_verified_at,
    last_login_at,
    last_seen_at,
    metadata,
    created_at,
    updated_at
"""

USER_FIELDS_QUALIFIED = """
    u.id::text AS id,
    u.email,
    u.display_name,
    u.role,
    u.status,
    u.email_verified_at,
    u.last_login_at,
    u.last_seen_at,
    u.metadata,
    u.created_at,
    u.updated_at
"""


def create_user(
    connection: Connection[Any],
    *,
    email: str,
    display_name: str,
    role: str,
) -> dict[str, Any]:
    return execute_one(
        connection,
        f"""
        INSERT INTO users (email, display_name, role)
        VALUES (%s, %s, %s)
        RETURNING
            {USER_FIELDS}
        """,
        (email, display_name, role),
    )


def get_user_by_id(connection: Connection[Any], user_id: str) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {USER_FIELDS}
        FROM users
        WHERE id::text = %s
        """,
        (user_id,),
    )


def get_user_by_email(connection: Connection[Any], email: str) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {USER_FIELDS}
        FROM users
        WHERE email = %s
        """,
        (email,),
    )


def get_user_by_email_with_credentials(
    connection: Connection[Any], email: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {USER_FIELDS_QUALIFIED},
            uac.password_hash
        FROM users u
        LEFT JOIN user_auth_credentials uac
            ON uac.user_id = u.id AND uac.credential_type = 'password'
        WHERE u.email = %s
        """,
        (email,),
    )


def list_users(
    connection: Connection[Any], limit: int, offset: int
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {USER_FIELDS}
        FROM users
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )


def count_users(connection: Connection[Any]) -> int:
    row = fetch_one(connection, "SELECT COUNT(*) AS total FROM users")
    return int(row["total"]) if row else 0


def set_user_role(
    connection: Connection[Any], user_id: str, role: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        UPDATE users
        SET role = %s, updated_at = NOW()
        WHERE id::text = %s
        RETURNING
            {USER_FIELDS}
        """,
        (role, user_id),
    )


def set_user_status(
    connection: Connection[Any], user_id: str, status: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        UPDATE users
        SET status = %s, updated_at = NOW()
        WHERE id::text = %s
        RETURNING
            {USER_FIELDS}
        """,
        (status, user_id),
    )


def update_last_login(connection: Connection[Any], user_id: str) -> None:
    fetch_all(
        connection,
        """
        UPDATE users
        SET last_login_at = NOW(), last_seen_at = NOW()
        WHERE id::text = %s
        RETURNING id
        """,
        (user_id,),
    )


def update_last_seen(connection: Connection[Any], user_id: str) -> None:
    fetch_all(
        connection,
        """
        UPDATE users
        SET last_seen_at = NOW()
        WHERE id::text = %s
        RETURNING id
        """,
        (user_id,),
    )


def update_user_display_name(
    connection: Connection[Any], user_id: str, display_name: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        UPDATE users
        SET display_name = %s, updated_at = NOW()
        WHERE id::text = %s
        RETURNING
            {USER_FIELDS}
        """,
        (display_name, user_id),
    )


def update_user_metadata(
    connection: Connection[Any], user_id: str, metadata: dict[str, Any]
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        UPDATE users
        SET metadata = %s, updated_at = NOW()
        WHERE id::text = %s
        RETURNING
            {USER_FIELDS}
        """,
        (Jsonb(metadata), user_id),
    )


def set_password_credential(
    connection: Connection[Any], user_id: str, password_hash: str
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO user_auth_credentials (user_id, credential_type, password_hash, password_updated_at)
        VALUES (%s, 'password', %s, NOW())
        ON CONFLICT (user_id, credential_type) DO UPDATE
        SET password_hash = EXCLUDED.password_hash,
            password_updated_at = NOW(),
            updated_at = NOW()
        RETURNING id::text AS id, user_id::text AS user_id, credential_type, password_updated_at
        """,
        (user_id, password_hash),
    )


def get_password_credential(
    connection: Connection[Any], user_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT id::text AS id, user_id::text AS user_id, password_hash, password_updated_at
        FROM user_auth_credentials
        WHERE user_id::text = %s AND credential_type = 'password'
        """,
        (user_id,),
    )


def update_password_credential(
    connection: Connection[Any], user_id: str, password_hash: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        UPDATE user_auth_credentials
        SET password_hash = %s, password_updated_at = NOW(), updated_at = NOW()
        WHERE user_id::text = %s AND credential_type = 'password'
        RETURNING id::text AS id, user_id::text AS user_id, password_updated_at
        """,
        (password_hash, user_id),
    )


def has_password_credential(connection: Connection[Any], user_id: str) -> bool:
    row = fetch_one(
        connection,
        """
        SELECT id
        FROM user_auth_credentials
        WHERE user_id::text = %s AND credential_type = 'password'
        """,
        (user_id,),
    )
    return row is not None


SESSION_FIELDS = """
    id::text AS id,
    user_id::text AS user_id,
    created_at,
    expires_at,
    revoked_at,
    last_seen_at,
    user_agent_hash,
    ip_hash,
    metadata
"""


def create_auth_session(
    connection: Connection[Any],
    *,
    user_id: str,
    token_hash: str,
    expires_at: datetime,
    user_agent_hash: str | None,
    ip_hash: str | None,
) -> dict[str, Any]:
    return execute_one(
        connection,
        f"""
        INSERT INTO auth_sessions (
            user_id, token_hash, expires_at, user_agent_hash, ip_hash
        ) VALUES (%s, %s, %s, %s, %s)
        RETURNING
            {SESSION_FIELDS}
        """,
        (user_id, token_hash, expires_at, user_agent_hash, ip_hash),
    )


def get_session_by_token_hash(
    connection: Connection[Any], token_hash: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {SESSION_FIELDS}
        FROM auth_sessions
        WHERE token_hash = %s
        """,
        (token_hash,),
    )


def get_active_session_by_token_hash(
    connection: Connection[Any], token_hash: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {SESSION_FIELDS}
        FROM auth_sessions
        WHERE token_hash = %s
          AND revoked_at IS NULL
          AND expires_at > NOW()
        """,
        (token_hash,),
    )


def touch_session(connection: Connection[Any], session_id: str) -> None:
    fetch_all(
        connection,
        """
        UPDATE auth_sessions
        SET last_seen_at = NOW()
        WHERE id::text = %s
        RETURNING id
        """,
        (session_id,),
    )


def revoke_session(
    connection: Connection[Any], session_id: str, user_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        UPDATE auth_sessions
        SET revoked_at = NOW()
        WHERE id::text = %s AND user_id::text = %s AND revoked_at IS NULL
        RETURNING
            {SESSION_FIELDS}
        """,
        (session_id, user_id),
    )


def revoke_all_user_sessions(connection: Connection[Any], user_id: str) -> int:
    rows = fetch_all(
        connection,
        """
        UPDATE auth_sessions
        SET revoked_at = NOW()
        WHERE user_id::text = %s AND revoked_at IS NULL
        RETURNING id
        """,
        (user_id,),
    )
    return len(rows)


def list_user_sessions(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {SESSION_FIELDS}
        FROM auth_sessions
        WHERE user_id::text = %s
        ORDER BY created_at DESC
        """,
        (user_id,),
    )


def count_active_sessions(connection: Connection[Any], user_id: str) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS total
        FROM auth_sessions
        WHERE user_id::text = %s AND revoked_at IS NULL AND expires_at > NOW()
        """,
        (user_id,),
    )
    return int(row["total"]) if row else 0


def cleanup_expired_sessions(
    connection: Connection[Any], limit: int
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        UPDATE auth_sessions
        SET revoked_at = NOW()
        WHERE revoked_at IS NULL
          AND expires_at <= NOW()
          AND id IN (
              SELECT id FROM auth_sessions
              WHERE revoked_at IS NULL AND expires_at <= NOW()
              LIMIT %s
          )
        RETURNING id::text AS id, user_id::text AS user_id, expires_at
        """,
        (limit,),
    )


def list_expired_unrevoked_sessions(
    connection: Connection[Any], limit: int
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT id::text AS id, user_id::text AS user_id, expires_at
        FROM auth_sessions
        WHERE revoked_at IS NULL AND expires_at <= NOW()
        LIMIT %s
        """,
        (limit,),
    )


TELEGRAM_LINK_FIELDS = """
    id::text AS id,
    user_id::text AS user_id,
    telegram_user_id,
    status,
    linked_at,
    unlinked_at,
    metadata
"""


def create_telegram_link(
    connection: Connection[Any], *, user_id: str, telegram_user_id: str
) -> dict[str, Any]:
    return execute_one(
        connection,
        f"""
        INSERT INTO user_telegram_links (user_id, telegram_user_id, status, linked_at)
        VALUES (%s, %s, 'linked', NOW())
        ON CONFLICT (telegram_user_id) DO UPDATE
        SET user_id = EXCLUDED.user_id,
            status = 'linked',
            linked_at = NOW(),
            unlinked_at = NULL
        RETURNING
            {TELEGRAM_LINK_FIELDS}
        """,
        (user_id, telegram_user_id),
    )


def get_telegram_link_by_user(
    connection: Connection[Any], user_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {TELEGRAM_LINK_FIELDS}
        FROM user_telegram_links
        WHERE user_id::text = %s AND status = 'linked'
        """,
        (user_id,),
    )


def get_telegram_link_by_telegram_user_id(
    connection: Connection[Any], telegram_user_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {TELEGRAM_LINK_FIELDS}
        FROM user_telegram_links
        WHERE telegram_user_id = %s AND status = 'linked'
        """,
        (telegram_user_id,),
    )


def unlink_telegram_user(
    connection: Connection[Any], user_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        UPDATE user_telegram_links
        SET status = 'unlinked', unlinked_at = NOW()
        WHERE user_id::text = %s AND status = 'linked'
        RETURNING
            {TELEGRAM_LINK_FIELDS}
        """,
        (user_id,),
    )


def list_telegram_links_for_admin(
    connection: Connection[Any], limit: int, offset: int
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {TELEGRAM_LINK_FIELDS}
        FROM user_telegram_links
        ORDER BY linked_at DESC
        LIMIT %s OFFSET %s
        """,
        (limit, offset),
    )
