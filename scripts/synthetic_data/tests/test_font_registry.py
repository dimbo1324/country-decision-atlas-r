from __future__ import annotations

import pytest
from scripts.synthetic_data.core.font_registry import (
    FontRegistryError,
    font_for_script,
)
from scripts.synthetic_data.core.locale_corpus import load_locale_corpus


def test_font_registered_for_every_script_used_by_the_locale_corpus() -> None:
    corpus = load_locale_corpus()
    scripts = {pack.profile.script for pack in corpus.packs}

    for script in scripts:
        font = font_for_script(script)
        assert font.file_path.exists()
        assert font.file_path.stat().st_size > 0


def test_each_registered_font_file_is_under_the_1mb_precommit_limit() -> None:
    corpus = load_locale_corpus()
    scripts = {pack.profile.script for pack in corpus.packs}

    for script in scripts:
        font = font_for_script(script)
        assert font.file_path.stat().st_size < 1024 * 1024


def test_unknown_script_raises_loudly_instead_of_falling_back() -> None:
    with pytest.raises(FontRegistryError):
        font_for_script("Klingon")
