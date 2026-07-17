from __future__ import annotations

from pathlib import Path
from pypdf import PdfReader
from utils.synthetic_data.core.random_content import RandomContentFactory
from utils.synthetic_data.generators.pdf.copyable import (
    PdfCopyableGenerator,
)


def test_pdf_copyable_text_is_extractable(
    tmp_path: Path, content: RandomContentFactory
) -> None:
    generator = PdfCopyableGenerator()
    artifact = generator.generate(output_dir=tmp_path, content=content)

    reader = PdfReader(str(artifact.path))
    extracted_text = "".join(page.extract_text() or "" for page in reader.pages)
    assert len(extracted_text.strip()) > 50
