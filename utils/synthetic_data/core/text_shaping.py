from __future__ import annotations

import arabic_reshaper
from bidi.algorithm import get_display
from collections.abc import Callable


_HAN_KANA_THAI_SCRIPTS = frozenset({"Han", "Han/Kana", "Thai"})


def shape_for_display(text: str, *, is_rtl: bool) -> str:
    """Convert logical-order text into the visual glyph order a left-to-right
    only renderer (reportlab's `drawString`) can draw correctly.

    For RTL scripts (Arabic, Persian) this reshapes letters into their
    joined presentation forms and reorders the whole string, including
    embedded Latin words, numbers, and URL stubs, via the Unicode
    Bidirectional Algorithm (spec section 8.3.5). For LTR text it is a
    no-op so callers can apply it unconditionally.
    """
    if not is_rtl:
        return text
    reshaped = arabic_reshaper.reshape(text)
    return str(get_display(reshaped))


def wrap_text(
    text: str,
    *,
    script: str,
    measure_width: Callable[[str], float],
    max_width: float,
) -> list[str]:
    """Wrap `text` to `max_width`, measuring each candidate line with
    `measure_width`.

    Space-delimited scripts wrap word-by-word. Han/Kana/Thai text has no
    reliable word-separating spaces, so it wraps character-by-character
    instead (spec section 8.3.7); wrapping a CJK/Thai string word-by-word
    would treat the entire paragraph as a single unbreakable "word" and
    overflow the page.
    """
    if script in _HAN_KANA_THAI_SCRIPTS:
        units = list(text)
        separator = ""
    else:
        units = text.split()
        separator = " "

    lines: list[str] = []
    current: list[str] = []
    for unit in units:
        candidate = separator.join([*current, unit])
        if measure_width(candidate) <= max_width or not current:
            current.append(unit)
        else:
            lines.append(separator.join(current))
            current = [unit]
    if current:
        lines.append(separator.join(current))
    return lines
