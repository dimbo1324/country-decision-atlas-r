from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from psycopg import connect
from psycopg.rows import dict_row
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
API_DIR = ROOT_DIR / "apps" / "api"
for import_path in (ROOT_DIR, API_DIR):
    import_path_str = str(import_path)
    if import_path_str not in sys.path:
        sys.path.insert(0, import_path_str)

from app.core.config import get_settings  # noqa: E402
from app.repositories import auth as repository  # noqa: E402
from app.services.auth import (  # noqa: E402
    hash_password,
    is_valid_email,
    normalize_email,
)


VALID_ROLES = ("user", "editor", "moderator", "admin", "owner")


def create_or_update_auth_user(
    connection: Any,
    *,
    email: str,
    password: str,
    role: str,
    display_name: str | None,
    update_role: bool,
) -> dict[str, Any]:
    settings = get_settings()
    normalized_email = normalize_email(email)
    if not is_valid_email(normalized_email):
        raise ValueError(f"invalid_email:{email}")
    if len(password) < settings.auth_password_min_length:
        raise ValueError(
            f"weak_password:min_length={settings.auth_password_min_length}"
        )
    if role not in VALID_ROLES:
        raise ValueError(f"invalid_role:{role}")

    existing = repository.get_user_by_email(connection, normalized_email)
    if existing is None:
        user = repository.create_user(
            connection,
            email=normalized_email,
            display_name=display_name or normalized_email,
            role=role,
        )
        repository.set_password_credential(
            connection, user["id"], hash_password(password)
        )
        action = "created"
    else:
        user = existing
        if display_name:
            user = (
                repository.update_user_display_name(
                    connection, user["id"], display_name
                )
                or user
            )
        if update_role and role != user["role"]:
            user = (
                repository.set_user_role(connection, user["id"], role) or user
            )
        repository.set_password_credential(
            connection, user["id"], hash_password(password)
        )
        action = "updated"

    return {
        "action": action,
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "display_name": user["display_name"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create or update a local auth user (owner/admin bootstrap)."
    )
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--role", default="user", choices=VALID_ROLES)
    parser.add_argument("--display-name", default=None)
    parser.add_argument("--update-role", action="store_true", default=False)
    args = parser.parse_args(argv)

    settings = get_settings()
    try:
        with connect(settings.database_url, row_factory=dict_row) as connection:
            result = create_or_update_auth_user(
                connection,
                email=args.email,
                password=args.password,
                role=args.role,
                display_name=args.display_name,
                update_role=args.update_role,
            )
            connection.commit()
    except ValueError as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1

    print(json.dumps({"ok": True, **result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
