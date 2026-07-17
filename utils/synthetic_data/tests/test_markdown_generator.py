from __future__ import annotations

from pathlib import Path
from utils.synthetic_data.core.random_content import RandomContentFactory
from utils.synthetic_data.generators.markdown_generator import (
    MarkdownGenerator,
)


def test_markdown_generator_writes_heading_and_table(
    tmp_path: Path, content: RandomContentFactory
) -> None:
    generator = MarkdownGenerator()
    artifact = generator.generate(output_dir=tmp_path, content=content)

    text = artifact.path.read_text(encoding="utf-8")
    assert text.startswith("# ")
    assert "## " in text
    assert "|" in text
