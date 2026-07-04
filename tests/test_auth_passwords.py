"""Password hashing: roundtrip verification, PBKDF2 format, and per-call salting."""

from app.services import auth as service


def test_hash_password_roundtrip_verifies_correct_password() -> None:
    encoded = service.hash_password("correct-horse-battery-staple")
    assert (
        service.verify_password("correct-horse-battery-staple", encoded) is True
    )


def test_hash_password_rejects_wrong_password() -> None:
    encoded = service.hash_password("correct-horse-battery-staple")
    assert service.verify_password("wrong-password", encoded) is False


def test_hash_password_uses_pbkdf2_sha256_format() -> None:
    encoded = service.hash_password("some-password")
    algorithm, iterations, salt, digest = encoded.split("$")
    assert algorithm == "pbkdf2_sha256"
    assert int(iterations) == service.PBKDF2_ITERATIONS
    assert len(salt) == 32
    assert len(digest) == 64


def test_hash_password_generates_unique_salt_per_call() -> None:
    first = service.hash_password("same-password")
    second = service.hash_password("same-password")
    assert first != second


def test_verify_password_rejects_none_hash() -> None:
    assert service.verify_password("anything", None) is False


def test_verify_password_rejects_empty_hash() -> None:
    assert service.verify_password("anything", "") is False


def test_verify_password_rejects_malformed_hash_missing_parts() -> None:
    assert (
        service.verify_password("anything", "pbkdf2_sha256$260000$salt")
        is False
    )


def test_verify_password_rejects_unknown_algorithm() -> None:
    malformed = "bcrypt$260000$abcd$" + "ef" * 32
    assert service.verify_password("anything", malformed) is False


def test_verify_password_rejects_non_numeric_iterations() -> None:
    malformed = "pbkdf2_sha256$not-a-number$abcd$" + "ef" * 32
    assert service.verify_password("anything", malformed) is False


def test_normalize_email_lowercases_and_strips() -> None:
    assert service.normalize_email("  User@Example.COM  ") == "user@example.com"


def test_is_valid_email_accepts_well_formed_address() -> None:
    assert service.is_valid_email("user@example.com") is True


def test_is_valid_email_rejects_missing_at_sign() -> None:
    assert service.is_valid_email("user.example.com") is False


def test_is_valid_email_rejects_missing_domain_dot() -> None:
    assert service.is_valid_email("user@example") is False


def test_is_valid_email_rejects_whitespace() -> None:
    assert service.is_valid_email("us er@example.com") is False


def test_generate_session_token_returns_unique_url_safe_tokens() -> None:
    first = service.generate_session_token()
    second = service.generate_session_token()
    assert first != second
    assert len(first) >= 32


def test_hash_session_token_is_deterministic_sha256() -> None:
    token = "raw-session-token"
    assert service.hash_session_token(token) == service.hash_session_token(
        token
    )
    assert len(service.hash_session_token(token)) == 64


def test_hash_session_token_differs_for_different_tokens() -> None:
    assert service.hash_session_token("token-a") != service.hash_session_token(
        "token-b"
    )
