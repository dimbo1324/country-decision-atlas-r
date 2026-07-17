from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from utils.synthetic_data.core.paths import DEFAULT_INPUT_DATA_FILE


class InputDataError(RuntimeError):
    pass


@dataclass(frozen=True)
class InputData:
    words: tuple[str, ...]
    headers: tuple[str, ...]


def _read_string_list(
    payload: dict[str, Any], key: str, path: Path
) -> tuple[str, ...]:
    raw_value = payload.get(key)
    if not isinstance(raw_value, list) or not raw_value:
        raise InputDataError(
            f"{path}: {key!r} must be a non-empty list of strings"
        )
    if not all(isinstance(item, str) and item.strip() for item in raw_value):
        raise InputDataError(
            f"{path}: {key!r} must contain only non-empty strings"
        )
    return tuple(raw_value)


def load_input_data(path: Path = DEFAULT_INPUT_DATA_FILE) -> InputData:
    if not path.exists():
        raise InputDataError(f"Input data file not found: {path}")

    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise InputDataError(f"{path}: invalid JSON ({error})") from error

    if not isinstance(payload, dict):
        raise InputDataError(f"{path}: root JSON value must be an object")

    return InputData(
        words=_read_string_list(payload, "words", path),
        headers=_read_string_list(payload, "headers", path),
    )
