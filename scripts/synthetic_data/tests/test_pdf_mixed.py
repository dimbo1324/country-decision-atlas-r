from __future__ import annotations

from pathlib import Path
from pypdf import PdfReader
from scripts.synthetic_data.core.random_content import RandomContentFactory
from scripts.synthetic_data.generators.pdf.mixed import PdfMixedGenerator


def test_pdf_mixed_has_both_text_and_image_pages(
    tmp_path: Path, content: RandomContentFactory
) -> None:
    generator = PdfMixedGenerator()
    artifact = generator.generate(output_dir=tmp_path, content=content)

    reader = PdfReader(str(artifact.path))
    assert len(reader.pages) >= 2

    extracted_text = "".join(page.extract_text() or "" for page in reader.pages)
    assert len(extracted_text.strip()) > 20
    assert any(list(page.images) for page in reader.pages)
