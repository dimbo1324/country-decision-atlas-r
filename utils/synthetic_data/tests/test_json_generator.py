from __future__ import annotations

import json
from pathlib import Path
from utils.synthetic_data.core.random_content import RandomContentFactory
from utils.synthetic_data.generators.json_generator import JsonGenerator


def test_json_generator_writes_valid_json(
    tmp_path: Path, content: RandomContentFactory
) -> None:
    generator = JsonGenerator()
    artifact = generator.generate(output_dir=tmp_path, content=content)

    assert artifact.path.exists()
    assert artifact.path.suffix == ".json"
    document = json.loads(artifact.path.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    assert document
