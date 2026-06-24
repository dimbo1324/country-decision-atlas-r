from app.core.errors import api_error


PUBLICATION_STATUSES: tuple[str, ...] = (
    "draft",
    "review",
    "published",
    "archived",
    "rejected",
)

_ALLOWED: dict[str, frozenset[str]] = {
    "draft": frozenset({"review", "rejected", "archived"}),
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
            422, "invalid_publication_transition", "invalid_publication_transition"
        )


def is_publish_transition(old_status: str, new_status: str) -> bool:
    return old_status != "published" and new_status == "published"


def audit_action_for_transition(old_status: str, new_status: str) -> str:
    return _AUDIT_ACTIONS.get((old_status, new_status), "updated")
