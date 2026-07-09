"""Double-submit CSRF decision logic used by csrf_protection_middleware."""

from app.bootstrap.app_factory import csrf_check_required, csrf_tokens_match


def test_csrf_required_for_cookie_authenticated_mutating_request() -> None:
    assert csrf_check_required(
        method="POST",
        path="/api/v1/auth/sessions/revoke-all",
        has_authorization_header=False,
        has_session_cookie=True,
    )


def test_csrf_not_required_for_get_requests() -> None:
    assert not csrf_check_required(
        method="GET",
        path="/api/v1/auth/sessions",
        has_authorization_header=False,
        has_session_cookie=True,
    )


def test_csrf_not_required_for_login_and_register() -> None:
    for path in ("/api/v1/auth/login", "/api/v1/auth/register"):
        assert not csrf_check_required(
            method="POST",
            path=path,
            has_authorization_header=False,
            has_session_cookie=False,
        )


def test_csrf_not_required_for_bearer_token_clients() -> None:
    assert not csrf_check_required(
        method="POST",
        path="/api/v1/auth/sessions/revoke-all",
        has_authorization_header=True,
        has_session_cookie=True,
    )


def test_csrf_not_required_without_session_cookie() -> None:
    assert not csrf_check_required(
        method="POST",
        path="/api/v1/auth/sessions/revoke-all",
        has_authorization_header=False,
        has_session_cookie=False,
    )


def test_csrf_tokens_match_requires_equal_nonempty_values() -> None:
    assert csrf_tokens_match("abc", "abc")
    assert not csrf_tokens_match("abc", "def")
    assert not csrf_tokens_match(None, "abc")
    assert not csrf_tokens_match("abc", None)
    assert not csrf_tokens_match("", "")
