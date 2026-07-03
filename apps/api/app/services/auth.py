from app.core.config import Settings, get_settings
from app.core.errors import api_error
from app.repositories import auth as repository
from app.services.feature_flags import is_feature_enabled_by_key
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
from psycopg import Connection
import re
import secrets
from typing import Any, cast


PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 260_000
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS
    )
    return f"{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${salt}${derived.hex()}"


def verify_password(password: str, encoded_hash: str | None) -> bool:
    if not encoded_hash:
        return False
    parts = encoded_hash.split("$")
    if len(parts) != 4:
        return False
    algorithm, iterations_str, salt, expected_hex = parts
    if algorithm != PBKDF2_ALGORITHM:
        return False
    try:
        iterations = int(iterations_str)
    except ValueError:
        return False
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    return hmac.compare_digest(derived.hex(), expected_hex)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email))


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _require_auth_feature_enabled(connection: Connection[Any]) -> None:
    if not is_feature_enabled_by_key(connection, "auth_enabled"):
        raise api_error(
            403,
            "feature_disabled",
            "Authentication is currently disabled.",
            {},
        )


def register_user(
    connection: Connection[Any],
    *,
    email: str,
    password: str,
    display_name: str,
) -> dict[str, Any]:
    settings = get_settings()
    _require_auth_feature_enabled(connection)
    if not settings.auth_registration_enabled:
        raise api_error(
            403,
            "feature_disabled",
            "Registration is currently disabled.",
            {},
        )
    normalized_email = normalize_email(email)
    if not is_valid_email(normalized_email):
        raise api_error(
            422, "invalid_email", "Email address is not valid.", {"email": email}
        )
    if len(password) < settings.auth_password_min_length:
        raise api_error(
            422,
            "weak_password",
            f"Password must be at least {settings.auth_password_min_length} characters.",
            {"min_length": settings.auth_password_min_length},
        )
    if repository.get_user_by_email(connection, normalized_email) is not None:
        raise api_error(
            409,
            "email_already_registered",
            "An account with this email already exists.",
            {"email": normalized_email},
        )
    user = repository.create_user(
        connection,
        email=normalized_email,
        display_name=display_name.strip() or normalized_email,
        role="user",
    )
    repository.set_password_credential(connection, user["id"], hash_password(password))
    return user


def _new_session_expiry(settings: Settings) -> datetime:
    return datetime.now(UTC) + timedelta(hours=settings.auth_session_ttl_hours)


def create_login_session(
    connection: Connection[Any],
    *,
    user_id: str,
    user_agent_hash: str | None = None,
    ip_hash: str | None = None,
) -> tuple[str, dict[str, Any]]:
    settings = get_settings()
    raw_token = generate_session_token()
    token_hash = hash_session_token(raw_token)
    session = repository.create_auth_session(
        connection,
        user_id=user_id,
        token_hash=token_hash,
        expires_at=_new_session_expiry(settings),
        user_agent_hash=user_agent_hash,
        ip_hash=ip_hash,
    )
    return raw_token, session


def login_user(
    connection: Connection[Any],
    *,
    email: str,
    password: str,
    user_agent_hash: str | None = None,
    ip_hash: str | None = None,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    _require_auth_feature_enabled(connection)
    normalized_email = normalize_email(email)
    user = repository.get_user_by_email_with_credentials(connection, normalized_email)
    if user is None or not verify_password(password, user.get("password_hash")):
        raise api_error(
            401,
            "invalid_credentials",
            "Invalid email or password.",
            {},
        )
    if user["status"] == "suspended":
        raise api_error(403, "user_suspended", "This account is suspended.", {})
    if user["status"] == "deleted":
        raise api_error(403, "user_deleted", "This account no longer exists.", {})
    repository.update_last_login(connection, user["id"])
    raw_token, session = create_login_session(
        connection,
        user_id=user["id"],
        user_agent_hash=user_agent_hash,
        ip_hash=ip_hash,
    )
    refreshed_user = repository.get_user_by_id(connection, user["id"])
    assert refreshed_user is not None
    return raw_token, refreshed_user, session


def logout_session(
    connection: Connection[Any], *, user_id: str, session_id: str
) -> None:
    repository.revoke_session(connection, session_id, user_id)


def validate_session_token(
    connection: Connection[Any], raw_token: str
) -> dict[str, Any]:
    token_hash = hash_session_token(raw_token)
    session = repository.get_active_session_by_token_hash(connection, token_hash)
    if session is None:
        maybe_expired = repository.get_session_by_token_hash(connection, token_hash)
        if maybe_expired is not None and maybe_expired["revoked_at"] is None:
            raise api_error(401, "auth_session_expired", "Session has expired.", {})
        raise api_error(401, "invalid_auth_token", "Session token is invalid.", {})
    user = repository.get_user_by_id(connection, session["user_id"])
    if user is None:
        raise api_error(401, "invalid_auth_token", "Session token is invalid.", {})
    if user["status"] == "suspended":
        raise api_error(403, "user_suspended", "This account is suspended.", {})
    if user["status"] == "deleted":
        raise api_error(403, "user_deleted", "This account no longer exists.", {})
    repository.touch_session(connection, session["id"])
    return {"user": user, "session": session}


def get_current_user_from_token(
    connection: Connection[Any], raw_token: str
) -> dict[str, Any]:
    return cast(dict[str, Any], validate_session_token(connection, raw_token)["user"])
