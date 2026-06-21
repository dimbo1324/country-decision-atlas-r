from __future__ import annotations

import re


_AI_GARBAGE_PATTERNS = [
    re.compile(r"as an ai language model", re.IGNORECASE),
    re.compile(r"i('m| am) (an |a )?ai", re.IGNORECASE),
    re.compile(r"i cannot (translate|help)", re.IGNORECASE),
    re.compile(r"(translation|here is the translation)\s*:", re.IGNORECASE),
    re.compile(r"^\s*(sure|certainly|of course|gladly)[,!.]", re.IGNORECASE),
]

_MIN_LENGTH = 2
_MAX_RATIO = 10.0
_MIN_RATIO = 0.1


def validate_translation(
    source_text: str,
    translated_text: str,
    source_locale: str,
    target_locale: str,
) -> tuple[bool, str | None]:
    if not translated_text or not translated_text.strip():
        return False, "translated_text is empty"

    cleaned = translated_text.strip()

    if len(cleaned) < _MIN_LENGTH:
        return False, f"translated_text too short: {len(cleaned)} chars"

    if (
        source_locale != target_locale
        and cleaned.lower() == source_text.strip().lower()
    ):
        return (
            False,
            "translated_text identical to source_text despite different locales",
        )

    src_len = len(source_text)
    if src_len > 0:
        ratio = len(cleaned) / src_len
        if ratio > _MAX_RATIO:
            return False, f"translated_text suspiciously long: ratio={ratio:.1f}"
        if ratio < _MIN_RATIO and src_len > 20:
            return False, f"translated_text suspiciously short: ratio={ratio:.2f}"

    for pattern in _AI_GARBAGE_PATTERNS:
        if pattern.search(cleaned[:200]):
            return (
                False,
                f"translated_text contains AI system noise: matched {pattern.pattern!r}",
            )

    src_numbers = set(re.findall(r"\b\d{4,}\b", source_text))
    for num in src_numbers:
        if num not in cleaned:
            return False, f"important number {num!r} missing from translation"

    return True, None
