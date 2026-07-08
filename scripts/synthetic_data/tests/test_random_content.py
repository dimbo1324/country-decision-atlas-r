from __future__ import annotations

import json
import random
from scripts.synthetic_data.core import random_content


def test_random_sentence_is_capitalized_and_punctuated(
    rng: random.Random,
) -> None:
    sentence = random_content.random_sentence(rng)
    assert sentence[0].isupper()
    assert sentence.endswith(".")


def test_random_paragraphs_returns_requested_count(rng: random.Random) -> None:
    paragraphs = random_content.random_paragraphs(rng, count=4)
    assert len(paragraphs) == 4
    assert all(paragraph for paragraph in paragraphs)


def test_random_table_shape(rng: random.Random) -> None:
    table = random_content.random_table(rng, row_count=6, column_count=3)
    assert len(table.headers) == 3
    assert len(table.rows) == 6
    assert all(len(row) == 3 for row in table.rows)


def test_random_json_document_is_json_serializable(
    rng: random.Random,
) -> None:
    document = random_content.random_json_document(rng)
    json.dumps(document)
    assert isinstance(document, dict)
    assert document
