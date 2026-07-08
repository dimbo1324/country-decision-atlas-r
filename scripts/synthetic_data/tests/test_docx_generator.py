from __future__ import annotations

import random
from docx import Document
from pathlib import Path
from scripts.synthetic_data.generators.docx_generator import DocxGenerator


def test_docx_generator_has_editable_text_and_embedded_image(
    tmp_path: Path,
) -> None:
    generator = DocxGenerator()
    artifact = generator.generate(output_dir=tmp_path, rng=random.Random(9))

    document = Document(str(artifact.path))
    editable_text = "\n".join(
        paragraph.text for paragraph in document.paragraphs
    )
    assert editable_text.strip()
    assert len(document.inline_shapes) >= 1
