from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
MESSAGES_DIR = ROOT_DIR / "apps" / "web" / "src" / "messages"
LOCALES = ("en", "ru")


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
            "Compare apps/web/src/messages/en.json and ru.json key sets "
            "and fail on any one-sided key (orphan translation)."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Accepted for consistency with other dev-tools scripts; "
        "this script only ever checks, there is no fix mode.",
    )
    parser.parse_args(argv)

    en_keys = flatten_keys(load_messages("en"))
    ru_keys = flatten_keys(load_messages("ru"))

    missing_in_ru = sorted(en_keys - ru_keys)
    missing_in_en = sorted(ru_keys - en_keys)

    if not missing_in_ru and not missing_in_en:
        print(
            f"i18n key parity OK: {len(en_keys)} keys match in en.json and ru.json."
        )
        return 0

    if missing_in_ru:
        print(
            f"Keys in en.json but missing from ru.json ({len(missing_in_ru)}):",
            file=sys.stderr,
        )
        for key in missing_in_ru:
            print(f"  - {key}", file=sys.stderr)
    if missing_in_en:
        print(
            f"Keys in ru.json but missing from en.json ({len(missing_in_en)}):",
            file=sys.stderr,
        )
        for key in missing_in_en:
            print(f"  - {key}", file=sys.stderr)
    print(
        "\napps/web/src/messages/en.json and ru.json are out of sync. "
        "Add the missing key(s) to both dictionaries.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
