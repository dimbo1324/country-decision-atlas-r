from __future__ import annotations

import random
from pathlib import Path
from pypdf import PdfReader
from scripts.synthetic_data.generators.pdf.noncopyable import (
    PdfNonCopyableGenerator,
)


def test_pdf_non_copyable_has_no_text_but_has_image(tmp_path: Path) -> None:
    generator = PdfNonCopyableGenerator()
    artifact = generator.generate(output_dir=tmp_path, rng=random.Random(13))

    reader = PdfReader(str(artifact.path))
    extracted_text = "".join(page.extract_text() or "" for page in reader.pages)
    assert extracted_text.strip() == ""

    assert any(list(page.images) for page in reader.pages)
