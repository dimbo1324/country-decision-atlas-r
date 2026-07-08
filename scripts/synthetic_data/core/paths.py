from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SYNTHETIC_DATA_ROOT = REPO_ROOT / "docs" / "synthetic_data"
DEFAULT_INPUT_DATA_DIR = SYNTHETIC_DATA_ROOT / "input_data"
DEFAULT_INPUT_DATA_FILE = DEFAULT_INPUT_DATA_DIR / "data.json"
DEFAULT_OUTPUT_DATA_ROOT = SYNTHETIC_DATA_ROOT / "output_data"
