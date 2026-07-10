from __future__ import annotations

import dataclasses
import json
import pytest
from pathlib import Path
from scripts.synthetic_data.core.locale_corpus import (
    REQUIRED_BLOCK_IDS,
    REQUIRED_LOCALES,
    LocaleCorpusError,
    load_locale_corpus,
)


def test_default_corpus_has_exactly_the_required_15_locales() -> None:
    corpus = load_locale_corpus()

    locales = {pack.locale for pack in corpus.packs}

    assert locales == set(REQUIRED_LOCALES)
    assert len(corpus.packs) == 15


def test_ar_sa_and_fa_ir_are_flagged_rtl_and_others_are_not() -> None:
    corpus = load_locale_corpus()

    rtl_locales = {pack.locale for pack in corpus.packs if pack.is_rtl}

    assert rtl_locales == {"ar-SA", "fa-IR"}


def test_every_pack_has_all_required_blocks_with_at_least_two_variants() -> (
    None
):
    corpus = load_locale_corpus()

    for pack in corpus.packs:
        assert set(pack.blocks) == set(REQUIRED_BLOCK_IDS)
        for block_id in REQUIRED_BLOCK_IDS:
            assert len(pack.blocks[block_id]) >= 2

        assert pack.fictional_notice.strip()
        assert pack.sample_short.strip()
        assert pack.sample_long.strip()
        assert pack.sample_diacritic.strip()
        assert pack.sample_mixed.strip()
        assert pack.sample_number.strip()
        assert pack.sample_date.strip()
        assert len(pack.given_names) >= 5
        assert len(pack.family_names) >= 5


def test_by_locale_raises_for_unknown_locale() -> None:
    corpus = load_locale_corpus()

    with pytest.raises(LocaleCorpusError):
        corpus.by_locale("xx-XX")


def test_missing_locale_is_rejected(tmp_path: Path) -> None:
    default = load_locale_corpus()
    payload = {
        "schema_version": "locale-corpus-v1",
        "locales": [
            _pack_to_payload(pack)
            for pack in default.packs
            if pack.locale != "ta-IN"
        ],
    }
    path = tmp_path / "locale_corpus.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(LocaleCorpusError, match="missing"):
        load_locale_corpus(path)


def test_pii_like_email_in_sample_text_is_rejected(tmp_path: Path) -> None:
    default = load_locale_corpus()
    en_pack = default.by_locale("en-US")
    bad_pack = dataclasses.replace(
        en_pack, sample_short="Contact real.person@gmail.com for details."
    )
    payload = {
        "schema_version": "locale-corpus-v1",
        "locales": [
            _pack_to_payload(bad_pack if pack.locale == "en-US" else pack)
            for pack in default.packs
        ],
    }
    path = tmp_path / "locale_corpus.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(LocaleCorpusError, match="e-mail"):
        load_locale_corpus(path)


def test_secret_keyword_in_block_variant_is_rejected(tmp_path: Path) -> None:
    default = load_locale_corpus()
    en_pack = default.by_locale("en-US")
    bad_blocks = dict(en_pack.blocks)
    bad_blocks["country_intro"] = (
        *bad_blocks["country_intro"],
        "The api_key for {country_name} is not real.",
    )
    bad_pack = dataclasses.replace(en_pack, blocks=bad_blocks)
    payload = {
        "schema_version": "locale-corpus-v1",
        "locales": [
            _pack_to_payload(bad_pack if pack.locale == "en-US" else pack)
            for pack in default.packs
        ],
    }
    path = tmp_path / "locale_corpus.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(LocaleCorpusError, match="secret"):
        load_locale_corpus(path)


def test_disallowed_url_in_sample_text_is_rejected(tmp_path: Path) -> None:
    default = load_locale_corpus()
    en_pack = default.by_locale("en-US")
    bad_pack = dataclasses.replace(
        en_pack, sample_mixed="See https://real-tracking-service.com/x for it."
    )
    payload = {
        "schema_version": "locale-corpus-v1",
        "locales": [
            _pack_to_payload(bad_pack if pack.locale == "en-US" else pack)
            for pack in default.packs
        ],
    }
    path = tmp_path / "locale_corpus.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(LocaleCorpusError, match="network address"):
        load_locale_corpus(path)


def _pack_to_payload(pack: object) -> dict[str, object]:
    return {
        "locale": pack.locale,  # type: ignore[attr-defined]
        "language_name": pack.profile.language_name,  # type: ignore[attr-defined]
        "script": pack.profile.script,  # type: ignore[attr-defined]
        "direction": pack.profile.direction,  # type: ignore[attr-defined]
        "language_group": pack.profile.language_group,  # type: ignore[attr-defined]
        "fictional_notice": pack.fictional_notice,  # type: ignore[attr-defined]
        "given_names": list(pack.given_names),  # type: ignore[attr-defined]
        "family_names": list(pack.family_names),  # type: ignore[attr-defined]
        "blocks": {k: list(v) for k, v in pack.blocks.items()},  # type: ignore[attr-defined]
        "comment_templates": list(pack.comment_templates),  # type: ignore[attr-defined]
        "sample_short": pack.sample_short,  # type: ignore[attr-defined]
        "sample_long": pack.sample_long,  # type: ignore[attr-defined]
        "sample_diacritic": pack.sample_diacritic,  # type: ignore[attr-defined]
        "sample_mixed": pack.sample_mixed,  # type: ignore[attr-defined]
        "sample_number": pack.sample_number,  # type: ignore[attr-defined]
        "sample_date": pack.sample_date,  # type: ignore[attr-defined]
    }
