"""Role-based access control primitives: role matching, required-role, and required-capability enforcement."""

import pytest
from app.core.auth import CurrentUser
from app.core.rbac import (
    ADMIN,
    EDITOR,
    MODERATOR,
    OWNER,
    USER,
    has_any_role,
    has_role,
    require_admin,
    require_capability,
    require_capability_or_roles,
    require_editor,
    require_moderator,
    require_owner,
    require_roles,
    require_user,
)
from app.services import capabilities as capabilities_service
from fastapi import HTTPException
from typing import Any, cast
from unittest.mock import MagicMock


def _user(role: str) -> CurrentUser:
    return CurrentUser(
        id=f"{role}-id",
        email=f"{role}@example.local",
        display_name=role.title(),
        role=role,
        status="active",
    )


def test_has_role_matches_exact_role() -> None:
    assert has_role(_user("editor"), "editor") is True
    assert has_role(_user("editor"), "admin") is False


def test_has_any_role_matches_membership() -> None:
    assert has_any_role(_user("moderator"), (MODERATOR, ADMIN, OWNER)) is True
    assert has_any_role(_user("user"), (MODERATOR, ADMIN, OWNER)) is False


@pytest.mark.parametrize(
    ("dependency", "allowed_roles"),
    [
        (require_user, (USER, MODERATOR, EDITOR, ADMIN, OWNER)),
        (require_moderator, (MODERATOR, ADMIN, OWNER)),
        (require_editor, (EDITOR, ADMIN, OWNER)),
        (require_admin, (ADMIN, OWNER)),
        (require_owner, (OWNER,)),
    ],
)
def test_require_roles_allows_permitted_roles(
    dependency: Any, allowed_roles: tuple[str, ...]
) -> None:
    for role in allowed_roles:
        current_user = _user(role)
        assert dependency(current_user) is current_user


@pytest.mark.parametrize(
    ("dependency", "denied_roles"),
    [
        (require_moderator, (USER,)),
        (require_editor, (USER, MODERATOR)),
        (require_admin, (USER, MODERATOR, EDITOR)),
        (require_owner, (USER, MODERATOR, EDITOR, ADMIN)),
    ],
)
def test_require_roles_rejects_insufficient_roles(
    dependency: Any, denied_roles: tuple[str, ...]
) -> None:
    for role in denied_roles:
        with pytest.raises(HTTPException) as exc_info:
            dependency(_user(role))
        assert exc_info.value.status_code == 403
        detail = cast(dict[str, Any], exc_info.value.detail)
        assert detail["error"]["code"] == "insufficient_role"


def test_require_roles_error_details_include_role_and_required_roles() -> None:
    dependency = require_roles("admin", "owner")
    with pytest.raises(HTTPException) as exc_info:
        dependency(_user("editor"))
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["details"]["role"] == "editor"
    assert detail["error"]["details"]["required_roles"] == ["admin", "owner"]


def test_require_roles_custom_role_set() -> None:
    require_moderator_or_editor = require_roles(
        "moderator", "editor", "admin", "owner"
    )
    assert require_moderator_or_editor(_user("moderator")) is not None
    assert require_moderator_or_editor(_user("editor")) is not None
    with pytest.raises(HTTPException):
        require_moderator_or_editor(_user("user"))


def test_require_capability_allows_when_has_capability_true(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_service, "has_capability", lambda *_a, **_kw: True
    )
    dependency = require_capability("moderator.board")
    user = _user("user")

    result = dependency(connection=MagicMock(), current_user=user)

    assert result is user


def test_require_capability_denies_when_has_capability_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_service, "has_capability", lambda *_a, **_kw: False
    )
    dependency = require_capability("moderator.board")

    with pytest.raises(HTTPException) as exc_info:
        dependency(connection=MagicMock(), current_user=_user("user"))

    assert exc_info.value.status_code == 403
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "insufficient_capability"
    assert (
        detail["error"]["details"]["required_capability"] == "moderator.board"
    )
    assert detail["error"]["details"]["role"] == "user"


@pytest.mark.parametrize("role", [MODERATOR, EDITOR, ADMIN, OWNER])
def test_require_capability_or_roles_allows_listed_roles_without_db_lookup(
    role: str,
) -> None:
    dependency = require_capability_or_roles(
        "moderator.community", EDITOR, ADMIN, OWNER
    )
    user = _user(role)

    result = dependency(connection=MagicMock(), current_user=user)

    assert result is user


def test_require_capability_or_roles_allows_capability_grant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_service, "has_capability", lambda *_a, **_kw: True
    )
    dependency = require_capability_or_roles(
        "moderator.community", EDITOR, ADMIN, OWNER
    )
    user = _user("user")

    result = dependency(connection=MagicMock(), current_user=user)

    assert result is user


def test_require_capability_or_roles_denies_without_role_or_grant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        capabilities_service, "has_capability", lambda *_a, **_kw: False
    )
    dependency = require_capability_or_roles(
        "moderator.community", EDITOR, ADMIN, OWNER
    )

    with pytest.raises(HTTPException) as exc_info:
        dependency(connection=MagicMock(), current_user=_user("user"))

    assert exc_info.value.status_code == 403
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "insufficient_capability"
    assert detail["error"]["details"]["allowed_roles"] == [EDITOR, ADMIN, OWNER]
