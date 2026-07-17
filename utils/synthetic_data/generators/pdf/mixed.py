from __future__ import annotations

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from utils.synthetic_data.core.models import FileFormat
from utils.synthetic_data.core.random_content import RandomContentFactory
from utils.synthetic_data.core.text_image_renderer import (
    render_paragraphs_to_pages,
)
from utils.synthetic_data.generators.base import BaseGenerator
from utils.synthetic_data.generators.pdf._reportlab_text import (
    PAGE_HEIGHT,
    PAGE_WIDTH,
    draw_text_page,
)


class PdfMixedGenerator(BaseGenerator):
    """First page(s) hold real extractable text; a trailing page is a rendered picture with no text layer."""

    file_format = FileFormat.PDF_MIXED
    extension = "pdf"

    def _write(self, path: Path, content: RandomContentFactory) -> None:
        title = content.title()
        text_paragraphs = content.paragraphs(count=content.randint(2, 3))
        scanned_title = content.title()
        scanned_paragraphs = content.paragraphs(count=content.randint(2, 3))

        pdf_canvas = canvas.Canvas(str(path), pagesize=A4)
        draw_text_page(pdf_canvas, title, text_paragraphs)

        pdf_canvas.showPage()
        scanned_page = render_paragraphs_to_pages(
            [scanned_title, "", *scanned_paragraphs]
        )[0]
        pdf_canvas.drawImage(
            ImageReader(scanned_page),
            0,
            0,
            width=PAGE_WIDTH,
            height=PAGE_HEIGHT,
        )
        pdf_canvas.showPage()

        pdf_canvas.save()
