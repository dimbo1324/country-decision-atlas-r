from __future__ import annotations

import json
import random
from pathlib import Path
from scripts.synthetic_data.generators.json_generator import JsonGenerator


def test_json_generator_writes_valid_json(tmp_path: Path) -> None:
    generator = JsonGenerator()
    artifact = generator.generate(output_dir=tmp_path, rng=random.Random(42))

    assert artifact.path.exists()
    assert artifact.path.suffix == ".json"
    document = json.loads(artifact.path.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    assert document
