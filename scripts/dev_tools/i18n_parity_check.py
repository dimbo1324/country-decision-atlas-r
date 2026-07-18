from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
MESSAGES_DIR = ROOT_DIR / "apps" / "web" / "src" / "messages"
LOCALES = ("en", "ru", "es")


def load_messages(locale: str) -> dict[str, Any]:
    path = MESSAGES_DIR / f"{locale}.json"
    if not path.is_file():
        print(f"ERROR: missing messages file: {path}", file=sys.stderr)
        raise SystemExit(2)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: {path} is not valid JSON: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    if not isinstance(data, dict):
        print(
            f"ERROR: {path} must contain a JSON object at the top level.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return data


def flatten_keys(node: Any, prefix: str = "") -> set[str]:
    """Recursively collects dot-path keys, e.g. `auth.loginSubmit`. A leaf
    is any non-dict value (string, number, list, ...) -- only nested dicts
    are descended into, matching how next-intl resolves message keys."""
    if not isinstance(node, dict):
        return {prefix} if prefix else set()
    keys: set[str] = set()
    for key, value in node.items():
        path = f"{prefix}.{key}" if prefix else key
        keys |= flatten_keys(value, path)
    return keys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare apps/web/src/messages/{"
            + ",".join(LOCALES)
            + "}.json key sets and fail on any one-sided key (orphan translation)."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Accepted for consistency with other dev-tools scripts; "
        "this script only ever checks, there is no fix mode.",
    )
    parser.parse_args(argv)

    keys_by_locale = {
        locale: flatten_keys(load_messages(locale)) for locale in LOCALES
    }
    all_keys: set[str] = set()
    for keys in keys_by_locale.values():
        all_keys |= keys

    had_mismatch = False
    for locale, keys in keys_by_locale.items():
        missing = sorted(all_keys - keys)
        if missing:
            had_mismatch = True
            print(
                f"Keys missing from {locale}.json ({len(missing)}):",
                file=sys.stderr,
            )
            for key in missing:
                print(f"  - {key}", file=sys.stderr)

    if not had_mismatch:
        print(
            f"i18n key parity OK: {len(all_keys)} keys match across "
            f"{', '.join(f'{locale}.json' for locale in LOCALES)}."
        )
        return 0

    print(
        f"\napps/web/src/messages/{{{','.join(LOCALES)}}}.json are out of "
        "sync. Add the missing key(s) to every locale's dictionary.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
