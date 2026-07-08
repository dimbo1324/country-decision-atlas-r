from __future__ import annotations

import random
import string
from dataclasses import dataclass
from typing import Any


_WORD_BANK: tuple[str, ...] = (
    "aurora",
    "velvet",
    "harbor",
    "quartz",
    "meadow",
    "lantern",
    "cascade",
    "granite",
    "orchid",
    "thicket",
    "compass",
    "ember",
    "glacier",
    "willow",
    "pebble",
    "canyon",
    "driftwood",
    "marble",
    "horizon",
    "pinewood",
    "sparrow",
    "thunder",
    "violet",
    "cobalt",
    "amber",
    "ridge",
    "hollow",
    "brook",
    "cinder",
    "maple",
    "copper",
    "juniper",
    "prairie",
    "tundra",
    "basalt",
    "coral",
    "fern",
    "moss",
    "spruce",
    "clover",
    "hazel",
    "obsidian",
    "opal",
    "saffron",
    "slate",
    "topaz",
    "umbra",
    "wisteria",
    "zephyr",
    "acorn",
    "birch",
    "cedar",
    "delta",
    "ebony",
    "flint",
)

_HEADER_WORD_BANK: tuple[str, ...] = (
    "Overview",
    "Summary",
    "Findings",
    "Notes",
    "Appendix",
    "Reference",
    "Draft",
    "Sample",
    "Outline",
    "Fragment",
    "Snapshot",
    "Sketch",
)


def random_word(rng: random.Random) -> str:
    return rng.choice(_WORD_BANK)


def random_title(rng: random.Random, *, word_count: int = 3) -> str:
    words = [rng.choice(_HEADER_WORD_BANK)]
    words.extend(random_word(rng).capitalize() for _ in range(word_count - 1))
    return " ".join(words)


def random_sentence(
    rng: random.Random, *, min_words: int = 6, max_words: int = 14
) -> str:
    word_count = rng.randint(min_words, max_words)
    words = [random_word(rng) for _ in range(word_count)]
    return words[0].capitalize() + " " + " ".join(words[1:]) + "."


def random_paragraph(
    rng: random.Random, *, min_sentences: int = 3, max_sentences: int = 7
) -> str:
    sentence_count = rng.randint(min_sentences, max_sentences)
    return " ".join(random_sentence(rng) for _ in range(sentence_count))


def random_paragraphs(rng: random.Random, *, count: int) -> list[str]:
    return [random_paragraph(rng) for _ in range(count)]


def random_identifier(rng: random.Random, *, length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(rng.choice(alphabet) for _ in range(length))


@dataclass(frozen=True)
class RandomTable:
    headers: list[str]
    rows: list[list[str]]


def random_table(
    rng: random.Random, *, row_count: int = 8, column_count: int = 4
) -> RandomTable:
    headers = [f"Column {index + 1}" for index in range(column_count)]
    rows = [
        [
            (
                str(rng.randint(0, 10_000))
                if column_index % 2 == 0
                else random_word(rng).capitalize()
            )
            for column_index in range(column_count)
        ]
        for _ in range(row_count)
    ]
    return RandomTable(headers=headers, rows=rows)


def _random_scalar(rng: random.Random) -> Any:
    choice = rng.randint(0, 3)
    if choice == 0:
        return random_word(rng)
    if choice == 1:
        return rng.randint(-1_000, 1_000)
    if choice == 2:
        return round(rng.uniform(-100.0, 100.0), 3)
    return rng.choice([True, False])


def random_json_value(rng: random.Random, *, depth: int) -> Any:
    if depth <= 0:
        return _random_scalar(rng)

    kind = rng.randint(0, 4)
    if kind <= 2:
        return _random_scalar(rng)
    if kind == 3:
        return [
            random_json_value(rng, depth=depth - 1)
            for _ in range(rng.randint(1, 4))
        ]
    return {
        random_word(rng): random_json_value(rng, depth=depth - 1)
        for _ in range(rng.randint(1, 4))
    }


def random_json_document(
    rng: random.Random, *, depth: int = 3, field_count: int = 6
) -> dict[str, Any]:
    return {
        random_word(rng): random_json_value(rng, depth=depth)
        for _ in range(field_count)
    }
