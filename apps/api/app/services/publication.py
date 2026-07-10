from app.core.errors import api_error
from app.schemas.common import PublicationStatus


# Re-exported so existing importers of `PUBLICATION_STATUSES`/transition
# helpers from this module don't need a second import; the enum itself is
# defined once in app.schemas.common (P2-8, Аудит-эпизод 10 — this used to
# be a second, hand-duplicated tuple here).
PUBLICATION_STATUSES: tuple[str, ...] = tuple(
    status.value for status in PublicationStatus
)

_ALLOWED: dict[str, frozenset[str]] = {
    "draft": frozenset({"review", "rejected"}),
    "review": frozenset({"published", "rejected", "draft"}),
    "published": frozenset({"archived"}),
    "archived": frozenset({"published"}),
    "rejected": frozenset({"draft"}),
}

_AUDIT_ACTIONS: dict[tuple[str, str], str] = {
    ("draft", "review"): "submitted_for_review",
    ("review", "published"): "published",
    ("published", "archived"): "archived",
    ("review", "rejected"): "rejected",
    ("draft", "rejected"): "rejected",
    ("review", "draft"): "updated",
    ("rejected", "draft"): "updated",
    ("archived", "published"): "published",
}


def allowed_transition(old_status: str, new_status: str) -> bool:
    return new_status in _ALLOWED.get(old_status, frozenset())


def ensure_allowed_transition(old_status: str, new_status: str) -> None:
    if not allowed_transition(old_status, new_status):
        raise api_error(
            422,
            "invalid_publication_transition",
            "This status transition is not allowed.",
        )


def is_publish_transition(old_status: str, new_status: str) -> bool:
    return old_status != "published" and new_status == "published"


def audit_action_for_transition(old_status: str, new_status: str) -> str:
    return _AUDIT_ACTIONS.get((old_status, new_status), "updated")
