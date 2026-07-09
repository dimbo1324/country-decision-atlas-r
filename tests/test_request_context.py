"""Client IP resolution, device labeling, and IP masking for session visibility."""

from app.core.config import Settings
from app.core.request_context import (
    derive_device_label,
    mask_ip_for_display,
    resolve_client_ip,
)
from typing import Any
from unittest.mock import MagicMock


CHROME_WINDOWS_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
SAFARI_IPHONE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Mobile/15E148 Safari/604.1"
)
FIREFOX_LINUX_UA = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
)


def test_derive_device_label_recognizes_chrome_on_windows() -> None:
    assert derive_device_label(CHROME_WINDOWS_UA) == "Chrome on Windows"


def test_derive_device_label_recognizes_safari_on_ios() -> None:
    assert derive_device_label(SAFARI_IPHONE_UA) == "Safari on iOS"


def test_derive_device_label_recognizes_firefox_on_linux() -> None:
    assert derive_device_label(FIREFOX_LINUX_UA) == "Firefox on Linux"


def test_derive_device_label_handles_missing_user_agent() -> None:
    assert derive_device_label(None) == "Unknown device"
    assert derive_device_label("") == "Unknown device"


def test_mask_ip_for_display_masks_last_ipv4_octet() -> None:
    assert mask_ip_for_display("203.0.113.42") == "203.0.113.xxx"


def test_mask_ip_for_display_masks_ipv6() -> None:
    assert mask_ip_for_display("2001:db8:1234:5678::1") == "2001:db8::xxxx"


def test_mask_ip_for_display_handles_missing_ip() -> None:
    assert mask_ip_for_display(None) is None


def _request(*, client_host: str | None, forwarded_for: str = "") -> Any:
    request = MagicMock()
    request.client = MagicMock(host=client_host) if client_host else None
    request.headers = (
        {"X-Forwarded-For": forwarded_for} if forwarded_for else {}
    )
    return request


def test_resolve_client_ip_returns_none_without_client() -> None:
    settings = Settings(app_env="local")
    assert resolve_client_ip(_request(client_host=None), settings) is None


def test_resolve_client_ip_uses_direct_client_host_by_default() -> None:
    settings = Settings(app_env="local", trusted_proxy_headers=False)
    request = _request(client_host="10.0.0.5", forwarded_for="1.2.3.4")
    assert resolve_client_ip(request, settings) == "10.0.0.5"


def test_resolve_client_ip_trusts_forwarded_for_from_trusted_proxy() -> None:
    settings = Settings(
        app_env="local",
        trusted_proxy_headers=True,
        trusted_proxy_ips="10.0.0.5",
    )
    request = _request(client_host="10.0.0.5", forwarded_for="1.2.3.4, 5.6.7.8")
    assert resolve_client_ip(request, settings) == "1.2.3.4"


def test_resolve_client_ip_ignores_forwarded_for_from_untrusted_client() -> (
    None
):
    settings = Settings(
        app_env="local",
        trusted_proxy_headers=True,
        trusted_proxy_ips="10.0.0.9",
    )
    request = _request(client_host="10.0.0.5", forwarded_for="1.2.3.4")
    assert resolve_client_ip(request, settings) == "10.0.0.5"
