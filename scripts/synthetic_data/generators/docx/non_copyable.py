from __future__ import annotations

import io
from docx import Document
from pathlib import Path
from scripts.synthetic_data.core.models import FileFormat
from scripts.synthetic_data.core.random_content import RandomContentFactory
from scripts.synthetic_data.core.text_image_renderer import (
    render_paragraphs_to_pages,
)
from scripts.synthetic_data.generators.base import BaseGenerator


class DocxNonCopyableGenerator(BaseGenerator):
    """Every page is an embedded picture; the document has no real text runs at all."""

    file_format = FileFormat.DOCX_NON_COPYABLE
    extension = "docx"

    def _write(self, path: Path, content: RandomContentFactory) -> None:
        title = content.title()
        body = content.paragraphs(count=content.randint(3, 5))
        pages = render_paragraphs_to_pages([title, "", *body])

        document = Document()
        for page_image in pages:
            image_buffer = io.BytesIO()
            page_image.save(image_buffer, format="PNG")
            image_buffer.seek(0)
            document.add_picture(image_buffer)
        document.save(str(path))
