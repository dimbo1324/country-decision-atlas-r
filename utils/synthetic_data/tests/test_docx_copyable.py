from __future__ import annotations

from docx import Document
from pathlib import Path
from utils.synthetic_data.core.random_content import RandomContentFactory
from utils.synthetic_data.generators.docx.copyable import (
    DocxCopyableGenerator,
)


def test_docx_copyable_has_only_editable_text(
    tmp_path: Path, content: RandomContentFactory
) -> None:
    generator = DocxCopyableGenerator()
    artifact = generator.generate(output_dir=tmp_path, content=content)

    document = Document(str(artifact.path))
    editable_text = "\n".join(
        paragraph.text for paragraph in document.paragraphs
    )
    assert editable_text.strip()
    assert len(document.inline_shapes) == 0
