import hashlib
import hmac
import re
import secrets
from app.core.config import Settings, get_settings
from app.core.errors import api_error
from app.core.request_context import derive_device_label, mask_ip_for_display
from app.repositories import auth as repository, security_notifications
from app.repositories.audit import insert_audit_event
from app.services import rate_limiter
from app.services.feature_flags import ensure_feature_enabled
from datetime import UTC, datetime, timedelta
from psycopg import Connection, errors as psycopg_errors
from typing import Any, cast
from uuid import UUID


PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 260_000
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
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


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(24)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_device_identifier(value: str, settings: Settings) -> str:
    return hmac.new(
        settings.auth_device_fingerprint_salt.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _require_auth_feature_enabled(connection: Connection[Any]) -> None:
    ensure_feature_enabled(
        connection, "auth_enabled", "Authentication is currently disabled."
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
            422,
            "invalid_email",
            "Email address is not valid.",
            {"email": email},
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
    try:
        user = repository.create_user(
            connection,
            email=normalized_email,
            display_name=display_name.strip() or normalized_email,
            role="user",
        )
        repository.set_password_credential(
            connection, user["id"], hash_password(password)
        )
    except psycopg_errors.UniqueViolation as exc:
        raise api_error(
            409,
            "email_already_registered",
            "An account with this email already exists.",
            {"email": normalized_email},
        ) from exc
    return user


def _new_session_expiry(settings: Settings) -> datetime:
    return datetime.now(UTC) + timedelta(hours=settings.auth_session_ttl_hours)


def create_login_session(
    connection: Connection[Any],
    *,
    user_id: str,
    user_agent: str | None = None,
    client_ip: str | None = None,
    notify_new_device: bool = True,
) -> tuple[str, dict[str, Any], bool]:
    settings = get_settings()
    raw_token = generate_session_token()
    token_hash = hash_session_token(raw_token)
    user_agent_hash = (
        hash_device_identifier(user_agent, settings) if user_agent else None
    )
    ip_hash = hash_device_identifier(client_ip, settings) if client_ip else None
    device_label = derive_device_label(user_agent)
    ip_display = mask_ip_for_display(client_ip)
    device_fingerprint_hash = hash_device_identifier(
        f"{user_agent or ''}|{client_ip or ''}", settings
    )
    is_new_device = notify_new_device and not (
        repository.has_prior_session_with_fingerprint(
            connection, user_id, device_fingerprint_hash
        )
    )
    session = repository.create_auth_session(
        connection,
        user_id=user_id,
        token_hash=token_hash,
        expires_at=_new_session_expiry(settings),
        user_agent_hash=user_agent_hash,
        ip_hash=ip_hash,
        device_label=device_label,
        ip_display=ip_display,
        device_fingerprint_hash=device_fingerprint_hash,
    )
    if is_new_device:
        security_notifications.create_new_device_login_notification(
            connection,
            user_id=user_id,
            session_id=session["id"],
            device_label=device_label,
            ip_display=ip_display,
        )
        insert_audit_event(
            connection,
            entity_type="auth_session",
            entity_id=UUID(session["id"]),
            action="new_device_login",
            changed_by=user_id,
            changes={"device_label": device_label, "ip_display": ip_display},
        )
    return raw_token, session, is_new_device


def login_user(
    connection: Connection[Any],
    *,
    email: str,
    password: str,
    user_agent: str | None = None,
    client_ip: str | None = None,
) -> tuple[str, dict[str, Any], dict[str, Any], bool]:
    _require_auth_feature_enabled(connection)
    normalized_email = normalize_email(email)
    if rate_limiter.is_login_locked_out(normalized_email):
        raise api_error(
            429,
            "too_many_login_attempts",
            "Too many failed login attempts. Try again later.",
            {},
        )
    user = repository.get_user_by_email_with_credentials(
        connection, normalized_email
    )
    if user is None or not verify_password(password, user.get("password_hash")):
        rate_limiter.record_login_failure(normalized_email)
        raise api_error(
            401,
            "invalid_credentials",
            "Invalid email or password.",
            {},
        )
    if user["status"] == "suspended":
        raise api_error(403, "user_suspended", "This account is suspended.", {})
    if user["status"] == "deleted":
        raise api_error(
            403, "user_deleted", "This account no longer exists.", {}
        )
    rate_limiter.clear_login_failures(normalized_email)
    repository.update_last_login(connection, user["id"])
    raw_token, session, is_new_device = create_login_session(
        connection,
        user_id=user["id"],
        user_agent=user_agent,
        client_ip=client_ip,
    )
    refreshed_user = repository.get_user_by_id(connection, user["id"])
    assert refreshed_user is not None
    return raw_token, refreshed_user, session, is_new_device


def logout_session(
    connection: Connection[Any], *, user_id: str, session_id: str
) -> None:
    repository.revoke_session(connection, session_id, user_id)


def _should_touch_session(session: dict[str, Any], settings: Settings) -> bool:
    last_seen_at = session.get("last_seen_at")
    if last_seen_at is None:
        return True
    threshold = timedelta(minutes=settings.auth_session_touch_interval_minutes)
    return bool(datetime.now(UTC) - last_seen_at >= threshold)


def _should_rotate_token(session: dict[str, Any], settings: Settings) -> bool:
    last_rotated = session.get("rotated_at") or session["created_at"]
    threshold = timedelta(
        minutes=settings.auth_session_rotation_interval_minutes
    )
    return bool(datetime.now(UTC) - last_rotated >= threshold)


def validate_session_token(
    connection: Connection[Any], raw_token: str
) -> dict[str, Any]:
    token_hash = hash_session_token(raw_token)
    result = repository.get_session_with_user_by_token_hash(
        connection, token_hash
    )
    if result is None or result["is_revoked"]:
        raise api_error(
            401, "invalid_auth_token", "Session token is invalid.", {}
        )
    if result["is_expired"]:
        raise api_error(401, "auth_session_expired", "Session has expired.", {})
    user = result["user"]
    session = result["session"]
    if user["status"] == "suspended":
        raise api_error(403, "user_suspended", "This account is suspended.", {})
    if user["status"] == "deleted":
        raise api_error(
            403, "user_deleted", "This account no longer exists.", {}
        )
    settings = get_settings()
    rotated_token: str | None = None
    if result["matched_current_token"]:
        if _should_rotate_token(session, settings):
            rotated_token = generate_session_token()
            repository.rotate_session_token(
                connection,
                session["id"],
                new_token_hash=hash_session_token(rotated_token),
                previous_token_hash=token_hash,
                previous_token_expires_at=datetime.now(UTC)
                + timedelta(
                    seconds=settings.auth_session_rotation_grace_seconds
                ),
            )
        elif _should_touch_session(session, settings):
            repository.touch_session(connection, session["id"])
    return {"user": user, "session": session, "rotated_token": rotated_token}


def get_current_user_from_token(
    connection: Connection[Any], raw_token: str
) -> dict[str, Any]:
    return cast(
        dict[str, Any], validate_session_token(connection, raw_token)["user"]
    )


def require_step_up_reauthentication(
    connection: Connection[Any], *, user_id: str, password: str
) -> None:
    credential = repository.get_password_credential(connection, user_id)
    if credential is None or not verify_password(
        password, credential.get("password_hash")
    ):
        raise api_error(
            401,
            "step_up_reauthentication_failed",
            "Please confirm your current password to continue.",
            {},
        )
