from __future__ import annotations

import random
from dataclasses import dataclass
from scripts.synthetic_data.core.input_data import InputData
from typing import Any


@dataclass(frozen=True)
class RandomTable:
    headers: list[str]
    rows: list[list[str]]


class RandomContentFactory:
    """Draws all placeholder content from an InputData word/header pool, never from hardcoded literals."""

    def __init__(self, *, rng: random.Random, input_data: InputData) -> None:
        self._rng = rng
        self._input_data = input_data

    def randint(self, minimum: int, maximum: int) -> int:
        return self._rng.randint(minimum, maximum)

    def word(self) -> str:
        return self._rng.choice(self._input_data.words)

    def header_word(self) -> str:
        return self._rng.choice(self._input_data.headers)

    def title(self, *, word_count: int = 3) -> str:
        words = [self.header_word()]
        words.extend(self.word().capitalize() for _ in range(word_count - 1))
        return " ".join(words)

    def sentence(self, *, min_words: int = 6, max_words: int = 14) -> str:
        word_count = self._rng.randint(min_words, max_words)
        words = [self.word() for _ in range(word_count)]
        return words[0].capitalize() + " " + " ".join(words[1:]) + "."

    def paragraph(
        self, *, min_sentences: int = 3, max_sentences: int = 7
    ) -> str:
        sentence_count = self._rng.randint(min_sentences, max_sentences)
        return " ".join(self.sentence() for _ in range(sentence_count))

    def paragraphs(self, *, count: int) -> list[str]:
        return [self.paragraph() for _ in range(count)]

    def table(
        self, *, row_count: int = 8, column_count: int = 4
    ) -> RandomTable:
        headers = [f"Column {index + 1}" for index in range(column_count)]
        rows = [
            [
                (
                    str(self._rng.randint(0, 10_000))
                    if column_index % 2 == 0
                    else self.word().capitalize()
                )
                for column_index in range(column_count)
            ]
            for _ in range(row_count)
        ]
        return RandomTable(headers=headers, rows=rows)

    def _random_scalar(self) -> Any:
        choice = self._rng.randint(0, 3)
        if choice == 0:
            return self.word()
        if choice == 1:
            return self._rng.randint(-1_000, 1_000)
        if choice == 2:
            return round(self._rng.uniform(-100.0, 100.0), 3)
        return self._rng.choice([True, False])

    def json_value(self, *, depth: int) -> Any:
        if depth <= 0:
            return self._random_scalar()

        kind = self._rng.randint(0, 4)
        if kind <= 2:
            return self._random_scalar()
        if kind == 3:
            return [
                self.json_value(depth=depth - 1)
                for _ in range(self._rng.randint(1, 4))
            ]
        return {
            self.word(): self.json_value(depth=depth - 1)
            for _ in range(self._rng.randint(1, 4))
        }

    def json_document(
        self, *, depth: int = 3, field_count: int = 6
    ) -> dict[str, Any]:
        return {
            self.word(): self.json_value(depth=depth)
            for _ in range(field_count)
        }
