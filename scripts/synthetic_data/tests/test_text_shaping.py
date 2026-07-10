from __future__ import annotations

import unicodedata
from scripts.synthetic_data.core.text_shaping import (
    shape_for_display,
    wrap_text,
)


def test_ltr_text_is_unchanged() -> None:
    text = "Test sample 123"

    assert shape_for_display(text, is_rtl=False) == text


def test_rtl_text_reorders_and_reshapes() -> None:
    logical = "اختبار عينة 123"

    shaped = shape_for_display(logical, is_rtl=True)

    assert shaped != logical
    # The digits stay in their own left-to-right run and end up first in
    # the visual order produced by the Unicode Bidi Algorithm.
    assert shaped.startswith("123")
    # Reshaping replaces base Arabic letters with joined presentation forms.
    assert not any(0x0600 <= ord(ch) <= 0x06FF for ch in shaped if ch.isalpha())


def test_rtl_shaping_preserves_all_non_space_characters() -> None:
    logical = "مرحبا 42"

    shaped = shape_for_display(logical, is_rtl=True)

    assert len(shaped.replace(" ", "")) == len(logical.replace(" ", ""))


def test_vietnamese_nfc_nfd_pair_normalizes_equal() -> None:
    nfc = unicodedata.normalize("NFC", "Việt Nam")
    nfd = unicodedata.normalize("NFD", "Việt Nam")

    assert nfc != nfd
    assert unicodedata.normalize("NFC", nfd) == nfc
    assert unicodedata.normalize("NFD", nfc) == nfd


def test_wrap_text_wraps_space_delimited_text_word_by_word() -> None:
    text = "one two three four five"

    lines = wrap_text(
        text,
        script="Latin",
        measure_width=lambda candidate: len(candidate),
        max_width=11,
    )

    assert lines == ["one two", "three four", "five"]


def test_wrap_text_wraps_han_script_character_by_character() -> None:
    text = "一二三四五六七八"

    lines = wrap_text(
        text,
        script="Han",
        measure_width=lambda candidate: len(candidate),
        max_width=3,
    )

    assert lines == ["一二三", "四五六", "七八"]


def test_wrap_text_never_drops_a_word_wider_than_max_width() -> None:
    text = "supercalifragilisticexpialidocious short"

    lines = wrap_text(
        text,
        script="Latin",
        measure_width=lambda candidate: len(candidate),
        max_width=5,
    )

    assert "".join(lines).replace(" ", "") == text.replace(" ", "")
