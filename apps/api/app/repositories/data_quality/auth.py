from app.repositories import data_quality as data_quality_repository
from psycopg import Connection
from typing import Any


def count_active_owners(connection: Connection[Any]) -> int:
    rows = data_quality_repository.fetch_all(
        connection,
        "SELECT COUNT(*)::int AS count FROM users WHERE role = 'owner' AND status = 'active'",
    )
    return int(rows[0]["count"]) if rows else 0


def list_users_with_invalid_role(connection: Connection[Any]) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, email, role
        FROM users
        WHERE role NOT IN ('user', 'editor', 'moderator', 'admin', 'owner')
        """,
    )


def list_users_with_invalid_status(connection: Connection[Any]) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, email, status
        FROM users
        WHERE status NOT IN ('active', 'suspended', 'deleted')
        """,
    )


def list_active_users_missing_password_credential(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT u.id::text AS id, u.email
        FROM users u
        WHERE u.status = 'active'
          AND NOT EXISTS (
              SELECT 1 FROM user_auth_credentials uac
              WHERE uac.user_id = u.id AND uac.credential_type = 'password'
          )
        """,
    )


def list_password_credentials_with_invalid_hash_format(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        r"""
        SELECT id::text AS id, user_id::text AS user_id
        FROM user_auth_credentials
        WHERE credential_type = 'password'
          AND password_hash IS NOT NULL
          AND password_hash !~ '^pbkdf2_sha256\$[0-9]+\$[^$]+\$[0-9a-f]+$'
        """,
    )


def list_suspended_or_deleted_users_with_active_sessions(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT s.id::text AS id, s.user_id::text AS user_id, u.status AS user_status
        FROM auth_sessions s
        JOIN users u ON u.id = s.user_id
        WHERE u.status IN ('suspended', 'deleted')
          AND s.revoked_at IS NULL
          AND s.expires_at > NOW()
        """,
    )


def list_expired_sessions_not_revoked(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, user_id::text AS user_id, expires_at
        FROM auth_sessions
        WHERE revoked_at IS NULL AND expires_at <= NOW()
        """,
    )


def list_sessions_with_empty_token_hash(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, user_id::text AS user_id
        FROM auth_sessions
        WHERE BTRIM(token_hash) = ''
        """,
    )
