from __future__ import annotations

import pytest
import random
from pathlib import Path


@pytest.fixture
def rng() -> random.Random:
    return random.Random(20260708)


@pytest.fixture
def output_root(tmp_path: Path) -> Path:
    return tmp_path / "synthetic_data"
