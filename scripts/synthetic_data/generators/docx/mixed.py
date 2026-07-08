from __future__ import annotations

import io
from docx import Document
from pathlib import Path
from scripts.synthetic_data.core.models import FileFormat
from scripts.synthetic_data.core.random_content import RandomContentFactory
from scripts.synthetic_data.core.text_image_renderer import render_text_snippet
from scripts.synthetic_data.generators.base import BaseGenerator


class DocxMixedGenerator(BaseGenerator):
    """Mixes real editable paragraphs with one embedded picture-of-text paragraph in a single file."""

    file_format = FileFormat.DOCX_MIXED
    extension = "docx"

    def _write(self, path: Path, content: RandomContentFactory) -> None:
        document = Document()
        document.add_heading(content.title(), level=1)

        for paragraph in content.paragraphs(count=content.randint(2, 3)):
            document.add_paragraph(paragraph)

        document.add_heading("Scanned fragment", level=2)
        image_text = content.paragraphs(count=1)[0]
        snippet_image = render_text_snippet(image_text)
        image_buffer = io.BytesIO()
        snippet_image.save(image_buffer, format="PNG")
        image_buffer.seek(0)
        document.add_picture(image_buffer)

        document.add_paragraph(content.paragraphs(count=1)[0])

        document.save(str(path))
