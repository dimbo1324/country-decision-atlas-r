import re
from app.core.config import Settings
from contextvars import ContextVar, Token
from fastapi import Request


_NO_REQUEST_ID = "-"
_request_id_var: ContextVar[str] = ContextVar(
    "request_id", default=_NO_REQUEST_ID
)


def bind_request_id(request_id: str) -> Token[str]:
    """Store request_id for the duration of this request so logging.Formatter
    subclasses (see core/logging_config.py) can stamp every log line without
    threading the value through every function call (P2-1, Аудит-эпизод 7)."""
    return _request_id_var.set(request_id)


def reset_request_id(token: Token[str]) -> None:
    _request_id_var.reset(token)


def get_request_id() -> str:
    """Returns "-" outside a request (startup/shutdown/background scripts),
    never raises — logging must never fail because of a missing context."""
    return _request_id_var.get()


_BROWSER_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"Edg/", "Edge"),
    (r"OPR/|Opera", "Opera"),
    (r"Chrome/", "Chrome"),
    (r"CriOS/", "Chrome"),
    (r"Firefox/|FxiOS/", "Firefox"),
    (r"Version/.*Safari/", "Safari"),
)

_OS_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"Windows NT", "Windows"),
    (r"iPhone|iPad|iPod", "iOS"),
    (r"Mac OS X", "macOS"),
    (r"Android", "Android"),
    (r"Linux", "Linux"),
)


def resolve_client_ip(request: Request, settings: Settings) -> str | None:
    if request.client is None:
        return None
    if (
        settings.trusted_proxy_headers
        and request.client.host in settings.trusted_proxy_ip_set
    ):
        forwarded = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        )
        if forwarded:
            return forwarded
    return request.client.host


def derive_device_label(user_agent: str | None) -> str:
    if not user_agent:
        return "Unknown device"
    browser = next(
        (
            name
            for pattern, name in _BROWSER_PATTERNS
            if re.search(pattern, user_agent)
        ),
        "Unknown browser",
    )
    os_name = next(
        (
            name
            for pattern, name in _OS_PATTERNS
            if re.search(pattern, user_agent)
        ),
        "unknown OS",
    )
    return f"{browser} on {os_name}"


def mask_ip_for_display(ip: str | None) -> str | None:
    if not ip:
        return None
    if ":" in ip:
        groups = ip.split(":")
        return ":".join(groups[:2]) + "::xxxx"
    octets = ip.split(".")
    if len(octets) == 4:
        return f"{octets[0]}.{octets[1]}.{octets[2]}.xxx"
    return ip
