from __future__ import annotations

import pytest
import random
from pathlib import Path
from scripts.synthetic_data.core.input_data import InputData
from scripts.synthetic_data.core.random_content import RandomContentFactory


@pytest.fixture
def rng() -> random.Random:
    return random.Random(20260708)


@pytest.fixture
def input_data() -> InputData:
    return InputData(
        words=("alpha", "bravo", "charlie", "delta", "echo", "foxtrot"),
        headers=("Overview", "Summary", "Notes"),
    )


@pytest.fixture
def content(rng: random.Random, input_data: InputData) -> RandomContentFactory:
    return RandomContentFactory(rng=rng, input_data=input_data)


@pytest.fixture
def output_root(tmp_path: Path) -> Path:
    return tmp_path / "output_data"
