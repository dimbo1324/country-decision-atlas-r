from __future__ import annotations

import json
import pytest
from pathlib import Path
from scripts.synthetic_data.core.input_data import (
    InputDataError,
    load_input_data,
)


def _write_data_file(tmp_path: Path, payload: object) -> Path:
    data_file = tmp_path / "data.json"
    data_file.write_text(json.dumps(payload), encoding="utf-8")
    return data_file


def test_load_input_data_reads_words_and_headers(tmp_path: Path) -> None:
    data_file = _write_data_file(
        tmp_path,
        {"words": ["alpha", "bravo"], "headers": ["Overview"]},
    )

    input_data = load_input_data(data_file)

    assert input_data.words == ("alpha", "bravo")
    assert input_data.headers == ("Overview",)


def test_load_input_data_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(InputDataError, match="not found"):
        load_input_data(tmp_path / "missing.json")


def test_load_input_data_invalid_json_raises(tmp_path: Path) -> None:
    data_file = tmp_path / "data.json"
    data_file.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(InputDataError, match="invalid JSON"):
        load_input_data(data_file)


def test_load_input_data_missing_key_raises(tmp_path: Path) -> None:
    data_file = _write_data_file(tmp_path, {"words": ["alpha"]})

    with pytest.raises(InputDataError, match="headers"):
        load_input_data(data_file)


def test_load_input_data_empty_list_raises(tmp_path: Path) -> None:
    data_file = _write_data_file(
        tmp_path, {"words": [], "headers": ["Overview"]}
    )

    with pytest.raises(InputDataError, match="words"):
        load_input_data(data_file)


def test_load_input_data_non_string_entry_raises(tmp_path: Path) -> None:
    data_file = _write_data_file(
        tmp_path, {"words": ["alpha", 42], "headers": ["Overview"]}
    )

    with pytest.raises(InputDataError, match="words"):
        load_input_data(data_file)
