from __future__ import annotations

from pathlib import Path
from pypdf import PdfReader
from utils.synthetic_data.core.random_content import RandomContentFactory
from utils.synthetic_data.generators.pdf.non_copyable import (
    PdfNonCopyableGenerator,
)


def test_pdf_non_copyable_has_no_text_but_has_image(
    tmp_path: Path, content: RandomContentFactory
) -> None:
    generator = PdfNonCopyableGenerator()
    artifact = generator.generate(output_dir=tmp_path, content=content)

    reader = PdfReader(str(artifact.path))
    extracted_text = "".join(page.extract_text() or "" for page in reader.pages)
    assert extracted_text.strip() == ""
    assert any(list(page.images) for page in reader.pages)
