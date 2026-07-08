from __future__ import annotations

import random
from pathlib import Path
from pypdf import PdfReader
from scripts.synthetic_data.generators.pdf.copyable import (
    PdfCopyableGenerator,
)


def test_pdf_copyable_text_is_extractable(tmp_path: Path) -> None:
    generator = PdfCopyableGenerator()
    artifact = generator.generate(output_dir=tmp_path, rng=random.Random(11))

    reader = PdfReader(str(artifact.path))
    extracted_text = "".join(page.extract_text() or "" for page in reader.pages)
    assert len(extracted_text.strip()) > 50
