"""Shared PII detection used by author metrics, migration board, and their data-quality checks (P2-8, Аудит-эпизод 10)."""

from app.services.pii_patterns import contains_pii


def test_detects_email() -> None:
    assert contains_pii("Reach me at person@example.com") is True


def test_detects_phone_number() -> None:
    assert contains_pii("Call +1 (555) 123-4567 anytime") is True


def test_detects_social_handle() -> None:
    assert contains_pii("Find me @some_handle on there") is True


def test_detects_url() -> None:
    assert contains_pii("See https://example.com for details") is True


def test_detects_bare_www_url() -> None:
    assert contains_pii("Visit www.example.com") is True


def test_clean_text_is_not_flagged() -> None:
    assert contains_pii("Computed from public statistics.") is False


def test_checks_all_provided_texts() -> None:
    assert contains_pii("Clean title", "Contact person@example.com") is True
    assert contains_pii("Clean title", "Also clean") is False


def test_empty_strings_are_not_flagged() -> None:
    assert contains_pii("", "") is False
