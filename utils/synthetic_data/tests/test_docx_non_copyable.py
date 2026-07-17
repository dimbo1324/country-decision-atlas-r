from __future__ import annotations

from docx import Document
from pathlib import Path
from utils.synthetic_data.core.random_content import RandomContentFactory
from utils.synthetic_data.generators.docx.non_copyable import (
    DocxNonCopyableGenerator,
)


def test_docx_non_copyable_has_no_text_but_has_images(
    tmp_path: Path, content: RandomContentFactory
) -> None:
    generator = DocxNonCopyableGenerator()
    artifact = generator.generate(output_dir=tmp_path, content=content)

    document = Document(str(artifact.path))
    editable_text = "\n".join(
        paragraph.text for paragraph in document.paragraphs
    )
    assert editable_text.strip() == ""
    assert len(document.inline_shapes) >= 1
