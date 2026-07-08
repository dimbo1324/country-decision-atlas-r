from __future__ import annotations

from pathlib import Path
from scripts.synthetic_data.core.models import FileFormat
from scripts.synthetic_data.core.random_content import RandomContentFactory
from scripts.synthetic_data.core.text_image_renderer import (
    render_paragraphs_to_pages,
)
from scripts.synthetic_data.generators.base import BaseGenerator


class PdfNonCopyableGenerator(BaseGenerator):
    file_format = FileFormat.PDF_NON_COPYABLE
    extension = "pdf"

    def _write(self, path: Path, content: RandomContentFactory) -> None:
        title = content.title()
        body = content.paragraphs(count=content.randint(3, 5))
        pages = render_paragraphs_to_pages([title, "", *body])

        first_page, *rest_pages = pages
        first_page.save(
            path, format="PDF", save_all=True, append_images=rest_pages
        )
