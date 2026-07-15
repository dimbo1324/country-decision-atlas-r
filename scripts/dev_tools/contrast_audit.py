"""WCAG contrast audit for the design-system text tokens.

Reads the color tokens straight from packages/ui/src/tokens/theme.css and
fails (exit 1) when a text token drops below its required contrast ratio
on any background token. c1/c2 carry body text (AA normal, 4.5:1); c3/c4
carry small meta/label text throughout the app, so they are held to the
same 4.5:1 floor rather than the large-text discount.
"""

from __future__ import annotations

import re
from pathlib import Path


THEME_CSS = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "ui"
    / "src"
    / "tokens"
    / "theme.css"
)

BACKGROUND_TOKENS = ("bg", "bg2", "bg3", "bg4")
TEXT_TOKEN_MINIMUMS = {
    "c1": 4.5,
    "c2": 4.5,
    "c3": 4.5,
    "c4": 4.5,
}


def parse_tokens(css: str) -> dict[str, str]:
    tokens: dict[str, str] = {}
    for name, value in re.findall(
        r"--color-([a-z0-9]+):\s*(#[0-9a-fA-F]{6})", css
    ):
        tokens[name] = value
    return tokens


def relative_luminance(hex_color: str) -> float:
    def channel(raw: str) -> float:
        value = int(raw, 16) / 255
        return (
            value / 12.92
            if value <= 0.04045
            else ((value + 0.055) / 1.055) ** 2.4
        )

    stripped = hex_color.lstrip("#")
    red = channel(stripped[0:2])
    green = channel(stripped[2:4])
    blue = channel(stripped[4:6])
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(foreground: str, background: str) -> float:
    first = relative_luminance(foreground)
    second = relative_luminance(background)
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


def main() -> int:
    tokens = parse_tokens(THEME_CSS.read_text(encoding="utf-8"))

    missing = [
        name
        for name in (*BACKGROUND_TOKENS, *TEXT_TOKEN_MINIMUMS)
        if name not in tokens
    ]
    if missing:
        print(f"contrast audit: tokens missing from theme.css: {missing}")
        return 1

    failures: list[str] = []
    for text_token, minimum in TEXT_TOKEN_MINIMUMS.items():
        for background_token in BACKGROUND_TOKENS:
            ratio = contrast_ratio(tokens[text_token], tokens[background_token])
            status = "OK" if ratio >= minimum else "FAIL"
            print(
                f"  [{status}] {text_token} ({tokens[text_token]}) on "
                f"{background_token} ({tokens[background_token]}): {ratio:.2f}:1 "
                f"(needs {minimum}:1)"
            )
            if ratio < minimum:
                failures.append(
                    f"{text_token} on {background_token} = {ratio:.2f}:1"
                )

    if failures:
        print(f"contrast audit FAILED: {len(failures)} pair(s) below minimum.")
        return 1

    print(
        "contrast audit OK: every text token passes on every background token."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
