from __future__ import annotations

import random
from pathlib import Path
from scripts.synthetic_data.generators.markdown_generator import (
    MarkdownGenerator,
)


def test_markdown_generator_writes_heading_and_table(tmp_path: Path) -> None:
    generator = MarkdownGenerator()
    artifact = generator.generate(output_dir=tmp_path, rng=random.Random(7))

    content = artifact.path.read_text(encoding="utf-8")
    assert content.startswith("# ")
    assert "## " in content
    assert "|" in content
