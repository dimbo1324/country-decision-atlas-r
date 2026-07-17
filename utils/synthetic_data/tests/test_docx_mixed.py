from __future__ import annotations

from docx import Document
from pathlib import Path
from utils.synthetic_data.core.random_content import RandomContentFactory
from utils.synthetic_data.generators.docx.mixed import DocxMixedGenerator


def test_docx_mixed_has_editable_text_and_embedded_image(
    tmp_path: Path, content: RandomContentFactory
) -> None:
    generator = DocxMixedGenerator()
    artifact = generator.generate(output_dir=tmp_path, content=content)

    document = Document(str(artifact.path))
    editable_text = "\n".join(
        paragraph.text for paragraph in document.paragraphs
    )
    assert editable_text.strip()
    assert len(document.inline_shapes) >= 1
