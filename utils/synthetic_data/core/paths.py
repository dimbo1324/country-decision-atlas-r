from __future__ import annotations

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT_DATA_DIR = PACKAGE_ROOT / "input_data"
DEFAULT_INPUT_DATA_FILE = DEFAULT_INPUT_DATA_DIR / "data.json"
DEFAULT_WORLD_INPUT_FILE = DEFAULT_INPUT_DATA_DIR / "world_config.json"
DEFAULT_OUTPUT_DATA_ROOT = REPO_ROOT / ".synthetic_data"
