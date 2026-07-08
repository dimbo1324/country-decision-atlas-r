from __future__ import annotations

import json
from scripts.synthetic_data.core.input_data import InputData
from scripts.synthetic_data.core.random_content import RandomContentFactory


def test_sentence_is_capitalized_and_punctuated(
    content: RandomContentFactory,
) -> None:
    sentence = content.sentence()
    assert sentence[0].isupper()
    assert sentence.endswith(".")


def test_paragraphs_returns_requested_count(
    content: RandomContentFactory,
) -> None:
    paragraphs = content.paragraphs(count=4)
    assert len(paragraphs) == 4
    assert all(paragraph for paragraph in paragraphs)


def test_table_shape(content: RandomContentFactory) -> None:
    table = content.table(row_count=6, column_count=3)
    assert len(table.headers) == 3
    assert len(table.rows) == 6
    assert all(len(row) == 3 for row in table.rows)


def test_json_document_is_json_serializable(
    content: RandomContentFactory,
) -> None:
    document = content.json_document()
    json.dumps(document)
    assert isinstance(document, dict)
    assert document


def test_word_is_drawn_from_input_data(
    content: RandomContentFactory, input_data: InputData
) -> None:
    assert content.word() in input_data.words


def test_header_word_is_drawn_from_input_data(
    content: RandomContentFactory, input_data: InputData
) -> None:
    assert content.header_word() in input_data.headers
